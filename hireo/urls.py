from django.urls import path

from hireo import views

urlpatterns = [
    path("", views.index, name='index'),
    path('messages/', views.messages, name="messages"),
    path('bookmarks/', views.bookmarks, name="bookmarks"),
    path('deactivate/', views.deactivate_account, name="deactivate_account"),

]