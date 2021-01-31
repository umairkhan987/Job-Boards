from rest_framework import generics, exceptions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User, Profile
from freelancers.models import Proposal
from hireo.api.pagination import GeneralPaginationClass
from .permissions import IsEmployer, IsValidUser
from .serializers import PostTaskSerializer, ProposalListSerializer, NotificationSerializer, ReviewProposalSerializer, \
    OfferSerializer
from ..models import PostTask
from hireo.api.serializers import PostTaskSerializer as TaskListSerializer


# TODO: test with file
class PostTaskView(generics.CreateAPIView):
    serializer_class = PostTaskSerializer
    permission_classes = (IsAuthenticated, IsEmployer)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyTaskList(generics.ListAPIView):
    serializer_class = TaskListSerializer
    permission_classes = (IsAuthenticated, IsEmployer)
    pagination_class = GeneralPaginationClass

    def get_queryset(self):
        queryset = PostTask.objects.filter(user=self.request.user).order_by('-created_at')
        sortBy = self.request.query_params.get("sortBy", None)
        if sortBy and sortBy != "relevance":
            queryset = queryset.filter(job_status__iexact=sortBy)
        else:
            order = ['In Progress', 'Pending', 'Completed']
            order = {key: i for i, key in enumerate(order)}
            queryset = sorted(queryset, key=lambda task: order.get(task.job_status, 0))
        return queryset


class EditTaskView(generics.UpdateAPIView):
    queryset = PostTask.objects.all()
    serializer_class = PostTaskSerializer
    permission_classes = (IsAuthenticated, IsEmployer, IsValidUser)
    lookup_field = "id"
    lookup_url_kwarg = "task_id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.job_status == "In Progress":
            return Response({"detail": "You can't perform this action because task is in progress."}, status=403)
        elif instance.job_status == "Completed":
            return Response({"detail": "You can't perform this action because task is completed."}, status=403)
        else:
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=400)


class DeleteTaskView(generics.DestroyAPIView):
    queryset = PostTask.objects.all()
    serializer_class = PostTaskSerializer
    permission_classes = (IsAuthenticated, IsEmployer, IsValidUser)
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.job_status == "In Progress" or instance.job_status == "Completed":
            return Response(
                {"detail": "Your are not permitted to perform this action. Only Pending task will be delete."},
                status=403)
        if instance.task_file:
            instance.task_file.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageProposalView(generics.ListAPIView):
    queryset = PostTask.objects.all()
    permission_classes = (IsAuthenticated, IsEmployer, IsValidUser)
    serializer_class = ProposalListSerializer
    pagination_class = GeneralPaginationClass

    def get_queryset(self):
        instance = get_object_or_404(PostTask, pk=self.kwargs.get("id"))
        sortBy = self.request.query_params.get("sortBy", None)
        queryset = instance.proposals.order_by("created_at")
        if sortBy == "HF":
            queryset = queryset.order_by('-rate')
        elif sortBy == "LF":
            queryset = queryset.order_by('rate')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.last().task.user != self.request.user:
            return Response({"detail": "You are not permitted to perform this action."})
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AcceptProposalView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    permission_classes = (IsAuthenticated, IsEmployer)
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        task = instance.task
        if task.user != self.request.user:
            return Response({"detail": "You are not permitted to perform this action."}, status=403)
        if task.proposals.filter(status="accepted").exists():
            return Response({"detail": "Sorry your are not assign this job to multiple user."}, status=403)
        if task.proposals.filter(status='completed').exists():
            return Response({"detail": "Your job is completed"}, status=403)

        instance.user.profile.total_hired += 1
        instance.task.job_status = 'In Progress'
        instance.status = "accepted"

        instance.user.profile.save()
        instance.task.save()
        instance.save()
        # TODO: add notification handler when proposal accepted
        return Response({"detail": "Proposal accepted"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def dashboard_view(request, *args, **kwargs):
    if not request.user.is_Employer:
        return Response({"detail": "Please login as freelancer."})

    user = User.objects.get(email=request.user.email)
    pending = user.tasks.filter(job_status__exact="Pending").count()
    total_Proposals = Proposal.objects.filter(task__in=request.user.tasks.all()).count()
    data = {"total_tasks": user.tasks.count(),
            "task_completed": user.task_completed(),
            "task_in_progress": user.task_InProgress(),
            "pending_task": pending,
            "total_proposal": total_Proposals,
            }

    notifications_list = request.user.notifications.all()
    paginator = PageNumberPagination()
    paginator.page_size = 4
    paginator_qs = paginator.paginate_queryset(notifications_list, request)
    notification_serializer = NotificationSerializer(paginator_qs, many=True)
    # TODO: change the notifications object and send string API
    context = {
        "data": data,
        "notifications": notification_serializer.data,
    }
    return paginator.get_paginated_response(context)


class ReviewView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEmployer]
    serializer_class = ProposalListSerializer
    pagination_class = GeneralPaginationClass

    def get_queryset(self):
        return Proposal.objects.filter(
            task__in=self.request.user.tasks.filter(job_status__exact="Completed"),
            status__exact='completed').order_by('-updated_at')


class PostReviewView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    permission_classes = [IsAuthenticated, IsEmployer]
    serializer_class = ReviewProposalSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.task.user != self.request.user:
            return Response({"detail": "You are not permitted to perform this action."}, status=403)
        # TODO: set notification handler
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)


class SendOfferView(generics.CreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def perform_create(self, serializer):
        id = int(serializer.validated_data.get("profile_id", None))
        profile = get_object_or_404(Profile, pk=id)
        serializer.save(profile=profile, sender=self.request.user)
