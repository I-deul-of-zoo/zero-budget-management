from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from .models import Category, Budgets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import jwt
from django.shortcuts import get_list_or_404
from .serializers import CategoryListSerializer, SetBudgetSerializer
from .models import Category, Budgets
from config import settings
from django.db import IntegrityError

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

class CategoryListAndSetBudgetsview(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                GenericAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryListSerializer
        return SetBudgetSerializer
    
    #update에만 필요
    def get_object(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        obj = get_list_or_404(Budgets, user_id=data['user_id'])
        return obj
    
    def create(self, request, *args, **kwargs):
        #넣고자 하는 값이 해당 user에 대한 category 존재 유무를 확인
        # 해당 부분은 복합키 설정 
        datas = {'objects':[]}
        categories = request.data['category']
        keys = categories.keys()
        values = categories.values()
        #해당 total은 새로운 category가 들어올 경우 변경되어야할 부분
        total = sum(values)
        
        request.data.pop('category', None)
        # category마다 데이터를 저장 해야합니다.
        for key, value in zip(keys, values):
            # request.data['category'] = Category.objects.get(name=key).pk
            # request.data['amount'] = value
            # request.data['ratio'] = value / total
            
            serializer = self.get_serializer(data=request.data)
            # 유효성 검증을 하기위해 modelserializer의 field값에 맞게 데이터를 넣어 줇니다.
            #유효성 검증 전에 field에 접근해야합니다.    
            serializer.initial_data['category'] = Category.objects.get(name=key).pk
            serializer.initial_data['amount'] = value
            serializer.initial_data['ratio'] = value / total
            
            serializer.is_valid(raise_exception=True)
            #우선은 Django에서 복합키를 지원하지 않는다.
            #일단 복합키로 지정해 놓는것이 가장 직관적인 방법이고 복잡하게 db에 접근하여 확인 할필요가없다
            #만약 db에 접근하는것이 복합키로 설정하는것보다 낫다고 판단되면 변경할 예정이며 더 나은 방법을 찾아봐야겠다
            #이 로직은 post를 통해 이미 있는 데이터를 넣지 않게 하기 위해 생성
            try:
                self.perform_create(serializer)
            except IntegrityError as e:
                error_message = str(e)
                
                # 중복 키 에러인 경우에 대한 처리
                if 'Duplicate entry' in error_message:
                    response_data = {'error': '중복되는 category가 이미 존재합니다. 해당 내용을 상세페이지에서 확인하고 변경해주세요'}
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

                # 다른 IntegrityError에 대한 기본적인 처리
                response_data = {'error': '데이터베이스 에러가 발생했습니다.'}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            headers = self.get_success_headers(serializer.data)
            datas['objects'].append(serializer.data)
        return Response(datas, status=status.HTTP_201_CREATED, headers=headers)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    