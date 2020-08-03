from django.urls import path

from . import views

urlpatterns = [
    path('freelancers/', views.findFreelancer, name="find_freelancer"),
    path('profile/<int:id>/', views.freelancerProfile, name='freelancer_profile'),
    path('postTask/', views.postATask, name="post_task"),
    path('tasks/', views.myTasks, name="my_tasks"),
    path('task/<int:id>/edit/', views.editTask, name='edit_task'),
    path('task/<int:id>/delete/', views.deleteTask, name='delete_task'),

]
