from django.urls import include, path
from .views import CategoryListAndSetBudgetsview, BudgetsRecommendView

app_name = "budgets"
# base_url: v1/auth/

urlpatterns = [
    path('', CategoryListAndSetBudgetsview.as_view(), name='budgets'),
    path('rec/', BudgetsRecommendView.as_view(), name='budgets_rec'),
]