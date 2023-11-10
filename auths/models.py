import string
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class User(AbstractUser):
    objects = CustomUserManager()
    username = models.CharField(max_length=30, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    ##user model에서 각 row를 식별해줄 key를 설정
    USERNAME_FIELD = 'username'
