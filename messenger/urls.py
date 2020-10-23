from django.urls import path

from . import views

urlpatterns = [
    path('messages/', views.messages, name="messages"),
    path('messages/<int:id>/', views.message_details, name="message_details"),
    path('messages/delete/', views.messages_delete, name="messages_delete"),
    path("messages/receive/", views.received_message, name="received_message"),
    path("messages/get_users_list/", views.get_users_list, name="get_users_list"),
    path("messages/mark_as_read_message/", views.mark_as_read_message, name="mark_as_read_message"),
    path("messages/get_users_from_inbox/", views.get_users_form_inbox, name="get_users_from_inbox"),
]
