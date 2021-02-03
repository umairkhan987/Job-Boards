from calendar import month_name

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.api.permissions import IsFreelancer
from employer.models import PostTask, Offers
from hireo.api.pagination import GeneralPaginationClass
from hireo.models import HitCount
from .permissions import IsValidUser
from .serializers import ProposalSerializer, OfferSerializer, ReviewSerializer, NotificationSerializer
from ..models import Proposal


class SubmitProposalView(generics.CreateAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated, IsFreelancer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data.get("task_id", None)
        task = get_object_or_404(PostTask, pk=id)
        if task.proposals.filter(user=request.user).exists():
            return Response({"detail": "You bid has already been submitted."}, status=status.HTTP_403_FORBIDDEN)
        serializer.validated_data['user'] = self.request.user
        serializer.validated_data['task'] = task
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyJobsView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated, IsFreelancer]
    pagination_class = GeneralPaginationClass

    def get_queryset(self):
        queryset = Proposal.objects.filter(user=self.request.user).select_related("task").exclude(
            task_id=None).order_by(
            '-updated_at')
        sortBy = self.request.query_params.get("sortBy", None)

        if sortBy != 'pending' and sortBy != "relevance" and sortBy:
            queryset = queryset.filter(status__iexact=sortBy)
        elif sortBy == "pending":
            queryset = queryset.filter(status__isnull=True)
        else:
            order = ['accepted', None, 'completed', 'cancelled']
            order = {key: i for i, key in enumerate(order)}
            queryset = sorted(queryset, key=lambda proposal: order.get(proposal.status, 0))
        return queryset


class DeleteProposalView(generics.DestroyAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated, IsFreelancer, IsValidUser]
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status is not None:
            return Response({"detail": "You are not permitted to delete this Proposal"}, status=403)
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)


# calculate rating
def calculate_profile_rating(user):
    user.profile.success_rate = user.profile.calculate_success_rate()
    user.profile.rating = user.profile.calculate_rating()
    user.profile.save()


class CancelJobView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    permission_classes = [IsAuthenticated, IsFreelancer, IsValidUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != "accepted":
            return Response({"detail": "your proposal has not been accepted yet."}, status=403)

        instance.task.job_status = "Pending"
        instance.status = "cancelled"
        instance.task.save()
        instance.save()

        calculate_profile_rating(self.request.user)

        # TODO: add notification handler when cancel job
        return Response({"detail": "Job cancelled"}, status=200)


class JobCompletedView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    permission_classes = [IsAuthenticated, IsFreelancer, IsValidUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != "accepted":
            return Response({"detail": "your proposal has not been accepted yet."}, status=403)

        instance.task.job_status = 'Completed'
        instance.user.profile.total_job_done += 1
        instance.status = 'completed'
        instance.task.save()
        instance.user.profile.save()
        instance.save()

        calculate_profile_rating(self.request.user)

        # TODO: add notification handler when job completed
        return Response({"detail": "Job Completed"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def dashboard_view(request, *args, **kwargs):
    if not request.user.is_Freelancer:
        return Response({"detail": "Please login as freelancer."})

    views = HitCount.objects.filter(profile=request.user.profile)
    month = request.user.profile.created_at.month
    data = [views.filter(created_at__month=((month + x) % 12) or 12).count() or '' for x in range(6)]
    labels = [month_name[((month + i) % 12) or 12] for i in range(6)]

    notifications_list = request.user.notifications.all()
    paginator = PageNumberPagination()
    paginator.page_size = 4
    paginator_qs = paginator.paginate_queryset(notifications_list, request)
    notification_serializer = NotificationSerializer(paginator_qs, many=True)

    context = {
        "task_bid_won": request.user.task_accepted(),
        "task_completed": request.user.task_completed(),
        "task_in_progress": request.user.task_InProgress(),
        "data": data,
        "labels": labels,
        "notifications": notification_serializer.data,
    }
    # TODO: change the notifications object and send string API
    return paginator.get_paginated_response(context)


class OfferView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsFreelancer]
    serializer_class = OfferSerializer
    pagination_class = GeneralPaginationClass

    def get_queryset(self):
        return Offers.objects.filter(profile=self.request.user.profile).order_by('-created_at')


class DeleteOfferView(generics.DestroyAPIView):
    queryset = Offers.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsFreelancer]
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.profile != self.request.user.profile:
            return Response({"detail": "You are not permitted to delete this offer"}, status=403)
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)


class ReviewsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsFreelancer]
    serializer_class = ReviewSerializer
    pagination_class = GeneralPaginationClass

    def get_queryset(self):
        queryset = Proposal.objects.filter(Q(user=self.request.user) & Q(task__isnull=False)).order_by("-updated_at")
        if queryset.exists():
            queryset = queryset.filter(Q(status__iexact="completed") & ~Q(rating=0.0))
        return queryset