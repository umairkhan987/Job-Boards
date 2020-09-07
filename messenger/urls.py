from django.urls import path

from . import views

urlpatterns = [
    path('messages/', views.messages, name="messages"),
    path('messages/<int:id>/details/', views.message_details, name="message_details"),
    path('messages/delete/', views.messages_delete, name="messages_delete"),
]
