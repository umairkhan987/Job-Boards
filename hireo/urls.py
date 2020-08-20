from django.urls import path

from hireo import views

urlpatterns = [
    path("", views.index, name='index'),
    path('messages/', views.messages, name="messages"),
    path('messages/<int:id>/details/', views.message_details, name="message_details"),
    path('messages/delete/', views.messages_delete, name="messages_delete"),
    path('bookmarks/', views.bookmarks, name="bookmarks"),
    path('offer/', views.send_offers, name="send_offer"),
    path('deactivate/', views.deactivate_account, name="deactivate_account"),

]