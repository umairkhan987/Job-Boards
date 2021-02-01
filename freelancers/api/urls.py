from django.urls import path

from . import views

urlpatterns = [
    path("freelancer/proposal/", views.SubmitProposalView.as_view(), name="submit_proposal_view"),
    path("freelancer/jobs/", views.MyJobsView.as_view(), name="my_jobs_view"),
    path("freelancer/proposal/<int:id>/", views.DeleteProposalView.as_view(), name="delete_proposal_view"),
    path("freelancer/cancel/job/<int:id>/", views.CancelJobView.as_view(), name="cancel_job_view"),
    path("freelancer/complete/job/<int:id>/", views.JobCompletedView.as_view(), name="complete_job_view"),
    path("freelancer/dashboard/", views.dashboard_view, name="dashboard_view"),
    path("freelancer/offers/", views.OfferView.as_view(), name="offers_view"),
    path("freelancer/offer/<int:id>/", views.DeleteOfferView.as_view(), name="delete_offer_view"),
    path("freelancer/reviews/", views.ReviewsView.as_view(), name="reviews_view"),
]