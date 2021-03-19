from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


urlpatterns = [
    # path("login/", views.login, name="login_api_view"),
    path("login/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("register/", views.register, name="register_api_view"),
    path("change_password/", views.ChangePasswordView.as_view(), name="change_password_view"),
    path("update_account/", views.UpdateAccountView.as_view(), name="update_account_view"),
    path("update_profile/", views.UpdateProfileView.as_view(), name="update_profile_view"),
]