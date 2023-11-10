import random
import string
from datetime import date
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

STRING_SEQUENCE = string.ascii_uppercase + string.digits # 새로운 인증 코드 생성


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    #일반 유저 생성
    def create_user(self, username,password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError("username은 필수 영역입니다.")
        #email 형태를 동일하게 만들기 위한 함수
        user = self.model(
            username=username,
            date_joined = timezone.now(),
            **extra_fields)
    
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    #관리자 유저 생성
    def create_superuser(self,username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username, password, **extra_fields)