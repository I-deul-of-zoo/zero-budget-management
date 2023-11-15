from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from .models import Category, Budgets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
import jwt
from django.shortcuts import get_list_or_404, get_object_or_404
from .serializers import CategoryListSerializer, SetBudgetSerializer, BudgetsRecommendSerializer
from .models import Category, Budgets
from expenditure.models import ReasonableExpenditure
from config import settings
from django.db import IntegrityError
from django.http import Http404
from rest_framework.views import exception_handler
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

from rest_framework.exceptions import APIException

    
class CategoryListAndSetBudgetsview(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                GenericAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Category.objects.all()
    
    # 해당 token을 가지고 오는 method
    def get_token(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        return data['user_id']
    # 
    #변경된 데이터가 있을때 해당 유저의 각 category 비율 조정
    def get_total(self, request):
        budgets = self.get_object(request)
        request.data['category']
        total = sum(list(budget.amount for budget in budgets) + list(request.data['category'].values()))
        return total
    
    def update_ratio(self, request, total):
        budgets = self.get_object(request)
        for budget in budgets:
            new_ratio = budget.amount / total
            Budgets.objects.filter(id=budget.id).update(ratio=new_ratio)
        
    
    def create_budget_entry(self, serializer):
        #우선은 Django에서 복합키를 지원하지 않는다.
        #일단 복합키로 지정해 놓는것이 가장 직관적인 방법이고 복잡하게 db에 접근하여 확인 할필요가없다
        #만약 db에 접근하는것이 복합키로 설정하는것보다 낫다고 판단되면 변경할 예정이며 더 나은 방법을 찾아봐야겠다
        #이 로직은 post를 통해 이미 있는 데이터를 넣지 않게 하기 위해 생성
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except IntegrityError as e:
            error_message = str(e)
            
            if 'Duplicate entry' in error_message:
                response_data = {'error': '중복되는 category가 이미 존재합니다. 해당 내용을 상세페이지에서 확인하고 변경해주세요'}
                raise ValidationError(response_data)
            else:
                raise DBException({'error': '데이터베이스 에러가 발생했습니다.'})
            
    def update_budget_entry(self, serializer):
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
    
    # 지출 update 함수
    def expenditure_create(self, request, cate_id, value, date_diff):
        ReasonableExpenditure.objects.create(
            user_id_id=self.get_token(request),
            category_id_id=cate_id,
            reasonable_amount = int(value // (int(date_diff) * 100)) * 100
        )
   
    # 적정 예산은 예산과 같이 무조건 들어 오기 때문에
    # 이전 적정 예산이 존재 했을때 update
    # 새로운 적정 예산 = (새로운 예산 - 이전예산) / 남은기간 + 원래 있던 적정 예산
    def expenditure_update(self, request, cate_id, value, date_diff):
        expenditure = ReasonableExpenditure.objects.filter(user_id_id=self.get_token(request)).get(category_id_id=cate_id)
        cal_reasonable = int((value - self.get_object(request).get(category_id=cate_id).amount) // (int(date_diff) * 100)) * 100 + expenditure.reasonable_amount
        expenditure.update(reasonable_amount=cal_reasonable)
    
    #날짜 차이 구하는 함수 
    def date_diff(self):
        now = datetime.now()
        after_month = now + relativedelta(months=1)
        return (after_month - now).days
    
    def date_diff_update(self, request, cate_id):
        start_date = self.get_object(request).get(category_id=cate_id).created_at
        after_month = start_date + relativedelta(months=1)
        now = datetime.now()
        return (after_month - now).days
    
    # generic view에 필요한 함수   
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryListSerializer
        return SetBudgetSerializer
    
    #update에만 필요
    def get_object(self, request):
        obj = Budgets.objects.filter(user_id=self.get_token(request))
        return obj
    #그냥 모든 category를 한꺼번에 update
    def create(self, request, *args, **kwargs):
        #넣고자 하는 값이 해당 user에 대한 category 존재 유무를 확인
        # 해당 부분은 복합키 설정 
        datas = {'objects':[]}
        categories = request.data['category']
        keys = categories.keys()
        
        #해당 total은 새로운 category가 들어올 경우 변경되어야할 부분
        total = self.get_total(request)
        
        date_diff = self.date_diff()
        
        request.data.pop('category', None)
        category_list = Category.objects.all()
        #category마다 데이터를 저장 해야합니다.
        #또한 현재 있는 데이터는 post말고 update로 처리해줌 
        for cat in category_list:
            if cat.name in keys:
                cate_id= cat.id
                
                #새로운 예산을 생성하기전 예산에 대한 cate_id 합리적인 예산 계산
                # request.data['category'] = Category.objects.get(name=key).pk
                # request.data['amount'] = value
                # request.data['ratio'] = value / total
                value = categories[cat.name]
                serializer = self.get_serializer(data=request.data)
                # 유효성 검증을 하기위해 modelserializer의 field값에 맞게 데이터를 넣어 줇니다.
                #유효성 검증 전에 field에 접근해야합니다.    
                serializer.initial_data['category'] = cate_id
                serializer.initial_data['amount'] = value
                serializer.initial_data['ratio'] = value / total
                
                self.create_budget_entry(serializer)
                datas['objects'].append(serializer.data)
                
                #이전 적정 금액이 존재 하지 않을때는 이전 예산도 없어서 0으로 생각하고 계간 하므로 예산이 db에 먼저 들어가도 상관업음
                self.expenditure_create(request, cate_id, value, date_diff)
            else:
                cate_id= cat.id
                serializer = self.get_serializer(data=request.data)
                # 유효성 검증을 하기위해 modelserializer의 field값에 맞게 데이터를 넣어 줇니다.
                #유효성 검증 전에 field에 접근해야합니다.    
                serializer.initial_data['category'] = cate_id
                serializer.initial_data['amount'] = 0
                serializer.initial_data['ratio'] = 0
                
                self.create_budget_entry(serializer)
                datas['objects'].append(serializer.data)
                
                #이전 적정 금액이 존재 하지 않을때는 이전 예산도 없어서 0으로 생각하고 계간 하므로 예산이 db에 먼저 들어가도 상관업음
                self.expenditure_create(request, cate_id, 0, date_diff)
        # 각 category가 유효한지 확인한 후 total 대비 비율 update
        # update시 다음과 같은 error가 발생
        '''
        {
            "error": "중복되는 category가 이미 존재합니다. 해당 내용을 상세페이지에서 확인하고 변경해주세요"
        }
        '''
        #unique_together을 UniqueConstraint로 변경
        self.update_ratio(request, total)
        
        headers = self.get_success_headers(datas)
        return Response(datas, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def update(self, request, *args, **kwargs):
        #넣고자 하는 값이 해당 user에 대한 category 존재 유무를 확인
        # 해당 부분은 복합키 설정 
        datas = {'objects':[]}
        categories = request.data['category']
        keys = categories.keys()
        values = categories.values()
        
        request.data.pop('category', None)
        partial = kwargs.pop('partial', False)
        instance = self.get_object(request)
        
        #category마다 데이터를 저장 해야합니다.
        for key, value in zip(keys, values):
            
            try:
                category = Category.objects.get(name=key)
                cate_id = category.pk
            except Category.DoesNotExist:
                # 커스텀 예외 발생
                raise CategoryNotFoundException(f"{key}은 DB에 존재하지 않는 Category입니다.")
            date_diff = self.date_diff_update(request, cate_id)
            self.expenditure_update(request, cate_id, value, date_diff)
            #새로운 
            # request.data['category'] = Category.objects.get(name=key).pk
            # request.data['amount'] = value
            # request.data['ratio'] = value / total
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            # 유효성 검증을 하기위해 modelserializer의 field값에 맞게 데이터를 넣어 줇니다.
            #유효성 검증 전에 field에 접근해야합니다.    
            serializer.initial_data['category'] = cate_id
            serializer.initial_data['amount'] = value
            
            self.update_budget_entry(serializer)
            datas['objects'].append(serializer.data)
        # 변경하고자한 모든 값이 변경된 후에 비율을 생성 
        total = sum(ins.amount for ins in instance)
        self.update_ratio(request, total)
        return Response(datas)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    

class BudgetsRecommendView(mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            GenericAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Budgets.objects.all()
    
    def get_token(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        return data['user_id']
    
    def update_budget_entry(self, serializer):
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SetBudgetSerializer
        return BudgetsRecommendSerializer
    
    # 지출 update 함수
    def expenditure_create(self, request, cate_id, value, date_diff):
        ReasonableExpenditure.objects.create(
            user_id_id=self.get_token(request),
            category_id_id=cate_id,
            reasonable_amount = int(value // (int(date_diff) * 100)) * 100
        )
    #이전에 존재 했던 적정 예산을 알려줍니다.
    # 적정 예산은 예산과 같이 무조건 들어 오기 때문에
    # 이전 적정 예산이 존재 했을때 update
    # 새로운 적정 예산 = (새로운 예산 - 이전예산) / 남은기간 + 원래 있던 적정 예산
    def expenditure_update(self, request, cate_id, value, date_diff):
        expenditure = ReasonableExpenditure.objects.filter(user_id_id=self.get_token(request)).get(category_id_id=cate_id)
        cal_reasonable = int((value - self.get_object(request).get(category_id=cate_id).amount) // (int(date_diff) * 100)) * 100 + expenditure.reasonable_amount
        expenditure.update(reasonable_amount=cal_reasonable)
    
    #날짜 차이 구하는 함수 
    def date_diff(self):
        now = datetime.now()
        after_month = now + relativedelta(months=1)
        return (after_month - now).days
    
    def date_diff_update(self, request, cate_id):
        start_date = self.get_object(request).get(category_id=cate_id).created_at
        after_month = start_date + relativedelta(months=1)
        now = datetime.now()
        return (after_month - now).days
    
    #기존 이용중인 유저들이 설정한 평균값 입니다. 
    def cal_ratio(self, request, category_name):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        
        if Category.objects.get(id=category_name).name == '기타':
            #해당 1 - user의 비율 합이 기타의 비율이 됩니다. 10퍼가 안되는 비율은 0이므로
            mean_ratio = 1 - sum(self.get_object(request).values_list('ratio', flat=True))
            return mean_ratio
        budgets =  Budgets.objects.filter(category_id=category_name)
        budgets = budgets.exclude(user_id=data['user_id']).values_list('ratio', flat=True)
        cnt = budgets.count()
        #해당 카테고리에대한 모든 비율값을 들고 옵니다.
        mean_ratio = sum(budgets) / cnt
        if mean_ratio < 0.1:
            return 0
        return mean_ratio
    
    def update_ratio(self, request, except_list):
        for exc in except_list:
            cat = Category.objects.get(id=exc)
            self.get_object(request).filter(category_id=exc).update(ratio=self.cal_ratio(request, cat.name))
            
    def get_object(self, request):
        obj = Budgets.objects.filter(user_id=self.get_token(request))
        return obj
    
    def create(self, request, *args, **kwargs):
        
        datas = {'objects':[]}
        # 자신이 한달 쓸 예산 총량 
        total = request.data.pop('total', None)
        #추천 비율
        date_diff = self.date_diff()
        category_list = Category.objects.all()
        except_list = set(self.get_object(request).values_list('category', flat=True))
        #category마다 데이터를 저장 해야합니다.
        #또한 현재 있는 데이터는 post말고 update로 처리해줌 
        for cat in category_list:
            if cat.id not in except_list:
            # request.data['category'] = Category.objects.get(name=key).pk
            # request.data['amount'] = value
            # request.data['ratio'] = value / total
                serializer = self.get_serializer(data=request.data)
                # 유효성 검증을 하기위해 modelserializer의 field값에 맞게 데이터를 넣어 줇니다.
                #유효성 검증 전에 field에 접근해야합니다.
                mean_ratio = self.cal_ratio(request, cat.pk)
                value = int(math.ceil(total * mean_ratio))
                
                serializer.initial_data['category'] = cat.pk
                serializer.initial_data['amount'] = value
                serializer.initial_data['ratio'] = mean_ratio
            
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                self.expenditure_create(request, cat.pk, value, date_diff)
                datas['objects'].append(serializer.data)
                
        for exc in except_list:
            mean_ratio = self.cal_ratio(request, exc)
            value = int(math.ceil(total * mean_ratio))
            date_diff = self.date_diff_update(request, exc)
            # 각 category가 현재 있는 category는 업데이트를 해줘야한다.
            self.expenditure_update(request, exc, value, date_diff)
        # 각 category가 유효한지 확인한 후 total 대비 비율 update
        self.update_ratio(request, except_list)
        headers = self.get_success_headers(datas)
        return Response(datas, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        datas = {'objects':[]}
        # 자신이 한달 쓸 예산 총량 
        total = request.data.pop('total', None)
        #추천 비율
        partial = kwargs.pop('partial', False)
        instance = self.get_object(request)
        category_list = Category.objects.all()
        #category마다 데이터를 저장 해야합니다.
        #또한 현재 있는 데이터는 post말고 update로 처리해줌 
        for cat in category_list:
            # request.data['category'] = Category.objects.get(name=key).pk
            # request.data['amount'] = value
            # request.data['ratio'] = value / total
            
            mean_ratio = self.cal_ratio(request, cat.pk)
            value = int(math.ceil(total * mean_ratio))
            date_diff = self.date_diff_update(request, cat.pk)
            self.expenditure_update(request, cat.pk, value, date_diff)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            # 유효성 검증을 하기위해 modelserializer의 field값에 맞게 데이터를 넣어 줇니다.
            #유효성 검증 전에 field에 접근해야합니다.
            serializer.initial_data['category'] = cat.pk
            serializer.initial_data['amount'] = value
            serializer.initial_data['ratio'] = mean_ratio
            
        
            serializer.is_valid(raise_exception=True)
            self.update_budget_entry(serializer)
            datas['objects'].append(serializer.data)
                
        return Response(datas)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
# 커스텀 예외 클래스 정의
class CategoryNotFoundException(Exception):
    pass
                
class DBException(APIException):
    status_code = 500
    default_detail = 'Internal Server Error'
    
#custom 예외처리
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, CategoryNotFoundException):
        # CategoryNotFoundException 예외를 처리하고 원하는 JSON 응답을 생성
        return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    return response