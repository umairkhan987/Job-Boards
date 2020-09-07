from django.urls import path

from notification import views

urlpatterns = [
    path("unread/", views.unread, name="unread"),
    path('mark-all-as-read/', views.mark_all_as_read, name="mark-all-as-read"),
]
