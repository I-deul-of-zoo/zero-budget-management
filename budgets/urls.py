from django.urls import include, path
from .views import CategoryListAndSetBudgetsview

app_name = "budgets"
# base_url: v1/auth/

urlpatterns = [
    path('', CategoryListAndSetBudgetsview.as_view(), name='budgets'),
]