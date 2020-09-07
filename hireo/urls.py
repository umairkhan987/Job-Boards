from django.urls import path

from hireo import views

urlpatterns = [
    path("", views.index, name='index'),

    path("tasks/", views.findTasks, name='find_tasks'),
    path('task/<int:id>/', views.view_task, name='view_task'),

    path('freelancers/', views.find_freelancer, name="find_freelancer"),
    path('freelancers/profile/<int:id>/', views.freelancer_profile, name='freelancer_profile'),

    path('bookmarks/', views.bookmarks, name="bookmarks"),
    path('offer/', views.send_offers, name="send_offer"),
    path('deactivate/', views.deactivate_account, name="deactivate_account"),

]