from django.urls import include, path
from .views import ExpenditureLCAPIView, ExpenditureCRUDAPIView


app_name = "expenditure"
# base_url: v1/auth/

urlpatterns = [
    path('', ExpenditureLCAPIView.as_view(), name='expend'),
    path('<int:pk>/', ExpenditureCRUDAPIView.as_view(), name='expend_id')
]