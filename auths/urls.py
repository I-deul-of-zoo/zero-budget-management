from django.urls import include, path
from .views import CustomLoginView


app_name = "auths"
# base_url: v1/auth/

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom-login'),
    path('', include('dj_rest_auth.urls'), name='dj_rest_auth'),
  #가입승인 url
    path('registration/', include('dj_rest_auth.registration.urls'), name='registration'),
]