from django.urls import path
from django.contrib.auth import views as auth_views

from accounts import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('settings/', views.settings, name="settings"),
    path('changePassword/', views.changePassword, name='change-password'),
    path('update/', views.updateAccount, name="update-account"),
    path('profile/', views.updateProfile, name="update-profile"),
    path('getProfile/', views.getProfile, name="get-profile"),
]
