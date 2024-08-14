from django.urls import path
from .views import (
    UserCreateView, UserSavingPlanListView, WeeklyAmountUpdateView,
    LoginAPI, UserSavingPlanDetailView, SavingPlanCreateView, GetUserView,
    LogoutUserView, GoogleLoginView, UserRegisterView, ActivateUserApiView)
from dj_rest_auth.registration.views import RegisterView, LoginView, VerifyEmailView # LogoutView, UserDetailView


urlpatterns = [
    path('user/register/', UserCreateView.as_view(), name='user-create'),
    path('user/login/', LoginAPI.as_view(), name='user-login'),
    path('user/get/', GetUserView.as_view(), name='get-user'),
    path('user/logout-now/', LogoutUserView.as_view(), name='user-logout'),
    path('user/savingplan/', UserSavingPlanListView.as_view(),
         name='savingplan-list'),
    path('user/savingplan/create/', SavingPlanCreateView.as_view(),
         name='savingplan-create'),
    path('weeklyamount/update/<int:pk>/',
         WeeklyAmountUpdateView.as_view(), name='weeklyamount-update'),
    path('user/savingplan/<int:pk>/', UserSavingPlanDetailView.as_view(),
         name='user-savingplan'),
    # Google OAuth2
    path('user/login/google/', GoogleLoginView.as_view(), name='google-login'),
    path('user/login/google/callback/', GoogleLoginView.as_view(), name='google-callback'),
    # Allauth
    path("user/register-auth/", UserRegisterView.as_view(), name="rest-register"),
    path("user/login-auth/", LoginView.as_view(), name="rest-login"),
#     path("user/logout-auth/", LogoutView.as_view(), name="rest-logout"),
#     path('user/', UserDetailView.as_view(), name='rest-user-detail'),
    # End Allauth
    path('user/activate/<uidb64>/<token>/', ActivateUserApiView.as_view(), name='activate-user'),
    
]
