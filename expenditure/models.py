from django.db import models
from django.contrib.auth import get_user_model
from budgets.models import Category
User = get_user_model()
# Create your models here.

class Expenditure(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    consumption_amount = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)
    is_except = models.BooleanField(default=False)
    
class ReasonableExpenditure(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    reasonable_amount = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)