from django.urls import path

from . import views

urlpatterns = [
    path('messages/', views.messages, name="messages"),
    path('messages/<int:id>/', views.message_details, name="message_details"),
    path('messages/delete/', views.messages_delete, name="messages_delete"),
    path("messages/receive/", views.received_message, name="received_message"),
]
