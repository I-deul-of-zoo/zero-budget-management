from rest_framework.serializers import ModelSerializer, SerializerMethodField, Serializer
from .models import Expenditure
import jwt
from config import settings
from django.db.models import Sum
from rest_framework import serializers
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

class ExpenditureListSerializers(ModelSerializer):
    total_expend = SerializerMethodField()
    total_expend_category = SerializerMethodField()
    
    def decode_token(self):
        token_str = self.context['request'].headers.get("Authorization").split(' ')[1]
        user_id = jwt.decode(token_str, SECRET_KEY, ALGORITHM)['user_id']
        return user_id
    
    def get_total_expend(self, obj):
        user_id = self.decode_token()
        return sum(Expenditure.objects.filter(user_id_id=user_id).exclude(is_except=True).values_list('consumption_amount', flat=True))
    
    def get_total_expend_category(self, obj):
        user_id = self.decode_token()
        tot = Expenditure.objects.filter(user_id_id=user_id).exclude(is_except=True)
        total_expend_category = tot.values('category_id').annotate(total_consumption=Sum('consumption_amount'))
        return total_expend_category
    
    class Meta:
        model = Expenditure
        fields = ['user_id', 'consumption_amount', 'category_id', 'content', 'is_except', 'total_expend', 'total_expend_category', 'created_at']
        read_only_fields = ['total_expend', 'total_expend_category', 'user_id',  'category_id', 'created_at']
        
        
class ExpenditureCreateSerializers(ModelSerializer):  
    class Meta:
        model = Expenditure
        fields = ['user_id', 'consumption_amount', 'category_id', 'content', 'is_except']
        extra_kwargs = {
            'is_except': {'write_only': True},
        }
        
class ExpenditureRUDSerializers(ModelSerializer):
    class Meta:
        model = Expenditure
        fields = ['user_id', 'consumption_amount', 'category_id', 'content', 'is_except']
        read_only_fields = ['user_id', 'category_id']
        
class ExpenditureRecSerializers(Serializer):
    user = serializers.IntegerField()
    total = serializers.IntegerField()
    category_total = serializers.DictField(child=serializers.IntegerField())
    datetime = serializers.DateField()
    content = serializers.CharField(max_length=200)
    
class ExpenditureNotiSerializers(Serializer):
    user = serializers.IntegerField()
    #오늘 전체 지출 금액
    total = serializers.IntegerField()
    #category별 오늘 지출 금액, 오늘 적정금액, 오늘 위험도 
    category_total = serializers.DictField(child=serializers.DictField(child=serializers.IntegerField()))
    datetime = serializers.DateField()