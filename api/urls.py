from django.urls import path
from .views import (
    UserCreateView, UserSavingPlanListView, WeeklyAmountUpdateView,
    LoginAPI, UserSavingPlanDetailView, SavingPlanCreateView)


urlpatterns = [
    path('user/register/', UserCreateView.as_view(), name='user-create'),
    path('user/login/', LoginAPI.as_view(), name='user-login'),
    path('user/savingplan/', UserSavingPlanListView.as_view(),
         name='savingplan-list'),
    path('user/savingplan/create/', SavingPlanCreateView.as_view(),
         name='savingplan-create'),
    path('weeklyamount/update/<int:pk>/',
         WeeklyAmountUpdateView.as_view(), name='weeklyamount-update'),
    path('user/savingplan/<int:pk>/', UserSavingPlanDetailView.as_view(),
         name='user-savingplan'),
]
