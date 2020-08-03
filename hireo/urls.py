from django.urls import path

from hireo import views

urlpatterns = [
    path("", views.index, name='index'),
]