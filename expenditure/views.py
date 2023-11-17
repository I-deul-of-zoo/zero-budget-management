from django.shortcuts import render
from .models import Expenditure, ReasonableExpenditure
from budgets.models import Category, Budgets
from rest_framework import status
# Create your views here.
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.generics import ListCreateAPIView, GenericAPIView
from .serializers import ExpenditureListSerializers, ExpenditureCreateSerializers, ExpenditureRUDSerializers, ExpenditureRecSerializers,ExpenditureNotiSerializers
from rest_framework.permissions import IsAuthenticated
from config import settings
from rest_framework.response import Response
from rest_framework.views    import APIView
import jwt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
'''
POST http://127.0.0.1:8000/api/expenditures/
{
    "consumption_amount": int,
    "category_id": str,
    "content": str,
    "is_except" : str
}
'''
class ExpenditureLCAPIView(ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Expenditure.objects.all()
    
    
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ExpenditureListSerializers
        return ExpenditureCreateSerializers
        
    def extract_user_id_in_toekn(self, request):
        try:
            token_str = request.headers.get("Authorization").split(' ')[1]
            data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
            user_id = data['user_id']
            return user_id
        except jwt.ExpiredSignatureError:
            # Handle token expiration
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            return None
        
    def filter_queryset(self, queryset):
    # 추가적인 필터를 적용
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        category = self.request.query_params.get('category_id', None)
        
        # 최소 금액 필터
        if min_amount is not None:
            queryset = queryset.filter(amount__gte=min_amount)

        # 최대 금액 필터
        if max_amount is not None:
            queryset = queryset.filter(amount__lte=max_amount)

        # 해당 category_id에 대한 목록
        if category is not None:
            queryset = queryset.filter(category_id_id=category)
        #기간을 필수로 탐색
        queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        category = Category.objects.get(name=request.data['category_id'])
        
        serializer = self.get_serializer(data=request.data)
        serializer.initial_data['user_id'] = self.extract_user_id_in_toekn(request)
        serializer.initial_data['category_id'] = category.pk
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class ExpenditureCRUDAPIView(RetrieveModelMixin,
                            UpdateModelMixin,
                            DestroyModelMixin,
                            GenericAPIView):
    
    permission_classes=[IsAuthenticated]
    queryset = Expenditure.objects.all()
    serializer_class = ExpenditureRUDSerializers
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ExpenditureRecAPIView(APIView):
    
    permission_class = [IsAuthenticated]
    
    def extract_user_id_in_toekn(self, request):
        try:
            token_str = request.headers.get("Authorization").split(' ')[1]
            data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
            user_id = data['user_id']
            return user_id
        except jwt.ExpiredSignatureError:
            # Handle token expiration
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            return None
        
    def get_objects(self, request):
        instance = ReasonableExpenditure.objects.filter(user_id_id=self.extract_user_id_in_toekn(request))
        return instance


    def get(self, request, *arg, **kwargs):
        data = {}
        now = datetime.now()
        before_one_day = (now - timedelta(days=1)).strftime("%Y-%m-%d")    
        
        category_list = Category.objects.all()
        
        #현재 예산에 대한 남은 날짜
        before_one_month = Budgets.objects.filter(user_id=self.extract_user_id_in_toekn(request)).first().created_at + relativedelta(months=1)
        remaining_date = (before_one_month - now).days
        
        queryset = Expenditure.objects.filter(created_at=before_one_day, created_at__lt=now.strftime("%Y-%m-%d"))
        total = 0
        default = 1000
        data['category_total'] = {}
        for cat in category_list:
            #전날 해당 category에 대한 지출
            expenditure = sum(queryset.filter(category_id_id=cat.pk).values_list('consumption_amount', flat=True))
            reasonable = self.get_objects(request).get(category_id_id=cat.pk).reasonable_amount
            data['content'] = "절약을 잘 실천하고 계세요! 오늘도 절약 도전"
            if reasonable < 0:
                reasonable = default
                data['content'] = "지출이 너무 많아요, 우리 줄일수 있도록 노력해봐요"
            if expenditure > reasonable:
                #초과한 값
                reasonable = reasonable - int((expenditure - reasonable) / (remaining_date * 100)) * 100
                self.get_objects.filter(category_id_id=cat.pk).update(reasonable_amount=reasonable)
                data['content'] = "조금 지출을 더 했지만 괜찮아요.다음은 적당히 쓰도록 노려 해봐요"
            data['category_total'][cat.pk] = reasonable
            total += reasonable
        data['user'] = self.extract_user_id_in_toekn(request)
        data['total'] = total
        data['datetime'] = now.strftime("%Y-%m-%d")
        
        serializer = ExpenditureRecSerializers(data)
        return Response(serializer.data)
    
class ExpenditureNotiAPIView(APIView):
    def extract_user_id_in_toekn(self, request):
        try:
            token_str = request.headers.get("Authorization").split(' ')[1]
            data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
            user_id = data['user_id']
            return user_id
        except jwt.ExpiredSignatureError:
            # Handle token expiration
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            return None
        
    def get_objects(self, request):
        instance = Expenditure.objects.filter(user_id_id=self.extract_user_id_in_toekn(request))
        return instance


    def get(self, request, *arg, **kwargs):
        data = {}
        now = datetime.now()
        after_one_day = (now + timedelta(days=1)).strftime("%Y-%m-%d")    
        
        category_list = Category.objects.all()
        
        #현재 예산에 대한 남은 날짜
        after_one_month = Budgets.objects.filter(user_id=self.extract_user_id_in_toekn(request)).first().created_at + relativedelta(months=1)
         
        #인가된 한 유저에 대한 오늘의 지출들을 알 수 있는 부분
        queryset = self.get_objects(request).filter(created_at=now.strftime("%Y-%m-%d"), created_at__lt=after_one_day)
        total = 0
        data['category_total'] = {}
        for cat in category_list:
            #오늘 지출 금액
            expenditure = sum(queryset.filter(category_id_id=cat.pk).values_list('consumption_amount', flat=True))
            #오늘 적정금액
            reasonable = ReasonableExpenditure.objects.filter(user_id_id=self.extract_user_id_in_toekn(request)).get(category_id_id=cat.pk).reasonable_amount
            
        
                
            data['category_total'][cat.pk]['오늘 지출 금액'] = expenditure
            data['category_total'][cat.pk]['오늘 적정 금액'] = reasonable
            data['category_total'][cat.pk]['위험도'] = int(expenditure / (reasonable * 10)) * 1000
            total += expenditure
        data['user'] = self.extract_user_id_in_toekn(request)
        data['total'] = total
        data['datetime'] = now.strftime("%Y-%m-%d")
        serializer = ExpenditureNotiSerializers(data)
        return Response(serializer.data)