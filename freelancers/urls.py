from django.urls import path

from . import views

urlpatterns = [
    path('tasks/', views.findTasks, name='find_tasks'),
    path('task/<int:id>/', views.view_task, name='view_task'),
    path('proposal/', views.submit_proposals, name="submit_proposals"),
    path('myProposals/', views.my_proposals, name="my_proposals"),
    path('proposal/<int:id>/delete/', views.delete_proposal, name="delete_proposal"),
    path('task/<int:id>/cancel/', views.cancel_task, name="cancel_task"),
    path('task/<int:id>/completed/', views.task_completed, name="task_completed"),
    path('dashboard/', views.dashboard, name='freelancer_dashboard'),
    path('offers/', views.offers, name="offers"),
    path('delete/<int:id>/offer/', views.delete_offer, name="delete_offer"),
]
