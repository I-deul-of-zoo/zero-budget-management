from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=4)
    
class Budgets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categies')
    amount = models.BigIntegerField(default=0)
    ratio = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        #unique_together은 두개의 field를 가지고 unique를 적용하기 위해 사용되어 진다
        #다만, 문제점은 post일 경우 해당 데이터 검증이 되지만 update작업이 허용되지 않을 수 있게 됩닏.
        # 그래서, Django doc에서는 해당 기능에대해 유연성과 확장성을 늘리기 위해 UniqueConstraint를 지원합니다.
        # unique_together = ('user', 'category')
        constraints = [
            models.UniqueConstraint(fields=['user', 'category'], name='unique_user_category'),
            # 다른 제약 조건들...
        ]