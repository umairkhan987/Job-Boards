from django.urls import path

from . import views

urlpatterns = [
    path('message/', views.SendMessageView.as_view(), name="send_message_view"),
    path('messages/<int:id>/', views.message_detail_view, name="message_detail_view"),
    path('message/<int:id>/', views.received_message_view, name="received_message_view"),
    path('message/<int:id>/delete/', views.delete_message_view, name="delete_message_view"),
    path('inbox/users/', views.GetUserListView.as_view(), name="user_list_view"),
]