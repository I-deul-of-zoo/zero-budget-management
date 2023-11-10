from rest_framework import serializers
from .models import CustomUserManager
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
##연습용 Serializer
from datetime import datetime
from django.contrib.auth import get_user_model

class CustomRegisterSerializer(RegisterSerializer):
    email=None
  

class CustomLoginSerializer(LoginSerializer):
    email=None