from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="api_index"),
    path("tasks/", views.TaskListApiView.as_view(), name="task_list_view"),
    path("task/<int:pk>/", views.task_detail_view, name="task_view"),
    path("freelancers/", views.FreelancersListApiView.as_view(), name="freelancer_list_view"),
    path("freelancer/<int:pk>/profile/", views.freelancer_profile, name="freelancer_profile_view"),
]