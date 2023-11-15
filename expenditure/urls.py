from django.urls import include, path
from .views import ExpenditureLCAPIView, ExpenditureCRUDAPIView, ExpenditureRecAPIView,ExpenditureNotiAPIView


app_name = "expenditure"
# base_url: v1/auth/

urlpatterns = [
    path('', ExpenditureLCAPIView.as_view(), name='expend'),
    path('<int:pk>/', ExpenditureCRUDAPIView.as_view(), name='expend_id'),
    path('rec/', ExpenditureRecAPIView.as_view(), name='expend'),
    path('noti/', ExpenditureNotiAPIView.as_view(), name='expend'),
]