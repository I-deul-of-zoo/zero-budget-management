import jwt
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, Budgets
from config import settings
from auths.models import User
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'


class SetBudgetSerializer(ModelSerializer):

    class Meta:
        model=Budgets
        fields = ['category', 'amount', 'ratio']
        extra_kwargs = {
            'amount' : {'write_only': True},
            'ratio': {'write_only': True},
        }
    
    def create(self, validated_data):
        print(validated_data)
        # 현재 요청을 보내는 사용자(user_id)를 추출
        # create는 get_object를 하지않고 바로 serialize한 후에 model에 저장 함으로 여기서 user_id를 꺼내줘야합
        token_str = self.context['request'].headers.get("Authorization").split(' ')[1]
        user_id = jwt.decode(token_str, SECRET_KEY, ALGORITHM)['user_id']
        
        # 모델 생성 및 저장
        # 객체를 불러와서 저장할 수도 있고
        # orm을 통해 ForeignKey 필드에 기본 키 값을 직접 할당하는 방식으로 지정할 수 있습니다.
        budget = Budgets(
            user_id=user_id,
            category_id=validated_data['category'].pk,
            amount=validated_data['amount'],
            ratio=validated_data['ratio']
        )
        budget.save()
        return budget
    
class CategoryListSerializer(ModelSerializer):
    class Meta:
        model=Category
        fields = '__all__'