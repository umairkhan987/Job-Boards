from django.urls import path

from . import views

urlpatterns = [
    path("employer/post_task/", views.PostTaskView.as_view(), name="post_task_view"),
    path("employer/my_tasks/", views.MyTaskList.as_view(), name="my_task_list_view"),
    path("employer/edit_task/<int:task_id>/", views.EditTaskView.as_view(), name="edit_task_view"),
    path("employer/delete_task/<int:id>/", views.DeleteTaskView.as_view(), name="delete_task_view"),
    path("employer/manage_proposal/<int:id>/", views.ManageProposalView.as_view(), name="manage_proposal_view"),
    path("employer/accept_proposal/<int:id>/", views.AcceptProposalView.as_view(), name="accept_proposal_view"),
    path("employer/dashboard/", views.dashboard_view, name="dashboard_view"),
    path("employer/reviews/", views.ReviewView.as_view(), name="reviews"),
    path("employer/review/<int:id>/", views.PostReviewView.as_view(), name="post_reviews_view"),
]