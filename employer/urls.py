from django.urls import path

from . import views

urlpatterns = [
    path('freelancers/', views.find_freelancer, name="find_freelancer"),
    path('profile/<int:id>/', views.freelancer_profile, name='freelancer_profile'),
    path('postTask/', views.post_a_task, name="post_task"),
    path('tasks/', views.my_tasks, name="my_tasks"),
    path('task/<int:id>/edit/', views.edit_task, name='edit_task'),
    path('task/<int:id>/delete/', views.delete_task, name='delete_task'),
    path('proposal/<int:id>/manage/', views.manage_proposal, name='manage_proposal')

]
