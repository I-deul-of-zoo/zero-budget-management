from django.db import models
from django.contrib.auth import get_user_model
from budgets.models import Category
User = get_user_model()
# Create your models here.


class ReasonableExpenditure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    reasonable_amount = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    #한 유저와 한 카테고리에 대한 합리적인 가격은 하나여야 합니다.
    constraints = [
            models.UniqueConstraint(fields=['user', 'category'], name='unique_user_category_expenditure'),
            # 다른 제약 조건들...
        ]
    
class Expenditure(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    reasonable = models.ForeignKey(ReasonableExpenditure, on_delete=models.CASCADE)
    consumption_amount = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)
    is_except = models.BooleanField(default=False)
    