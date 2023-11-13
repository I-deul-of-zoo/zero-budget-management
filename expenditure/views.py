from django.shortcuts import render
from .models import Expenditure
from budgets.models import Category
from rest_framework import status
# Create your views here.
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.generics import ListCreateAPIView, GenericAPIView
from .serializers import ExpenditureListSerializers, ExpenditureCreateSerializers, ExpenditureRUDSerializers
from rest_framework.permissions import IsAuthenticated
from config import settings
from rest_framework.response import Response
import jwt
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