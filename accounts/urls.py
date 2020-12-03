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

    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='Hireo/password_reset_form.html'), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="Hireo/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="Hireo/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="Hireo/password_reset_complete.html"), name="password_reset_complete"),
]
