import operator
from functools import reduce

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Profile, User
from employer.models import PostTask
from hireo.api.pagination import GeneralPaginationClass
from hireo.api.serializers import TasksSerializer, ProfileSerializer, ProposalSerializer, \
    WorkHistoryProposalSerializer, UserSerializer, ProfileBookmarkSerializer, TaskBookmarkSerializer, \
    BookmarkedSerializer
from hireo.models import Bookmark, HitCount


@swagger_auto_schema(tags=['Index'], method='GET')
@api_view(['GET'])
def index(request):
    try:
        tasks = PostTask.objects.all()
        total_task = tasks.count()
        tasks = tasks.exclude(job_status__exact="Completed").order_by('-created_at')[:5]
        tasks_serializers = TasksSerializer(tasks, many=True)
        freelancers = Profile.objects.select_related('user').all()
        total_profile = freelancers.count()
        freelancers = freelancers.filter(updated=True).order_by('-rating')[:6]
        freelancers_serializer = ProfileSerializer(freelancers, many=True)

        context = {
            "total_tasks_posted": total_task,
            "total_freelancers": total_profile,
            "tasks": tasks_serializers.data,
            "freelancers": freelancers_serializer.data,
        }
        return Response(context)
    except Exception as e:
        return Response({"detail": str(e)}, status=404)


class TaskListApiView(generics.ListAPIView):
    pagination_class = GeneralPaginationClass
    serializer_class = TasksSerializer
    queryset = PostTask.objects.exclude(job_status__exact="Completed").order_by('-created_at')

    def get_queryset(self):
        sortBy = self.request.query_params.get("sortBy", None)
        search = self.request.query_params.get("search", None)
        rate = self.request.query_params.get("rate", None)
        skills = self.request.query_params.getlist("skills", None)

        queryset = self.queryset
        if sortBy:
            if sortBy == "oldest":
                queryset = queryset.order_by('created_at')
            elif sortBy == "newest":
                queryset = queryset.order_by('-created_at')
        if search:
            queryset = queryset.filter(title__icontains=search)
        if rate:
            rate = rate.split(',')
            queryset = queryset.filter(Q(min_price__gte=rate[0]) & Q(max_price__lte=rate[1]))
        if skills:
            queryset = queryset.filter(reduce(operator.or_, (Q(skills__icontains=x) for x in skills)))
        return queryset


@api_view(['GET'])
def task_detail_view(request, pk, *args, **kwargs):
    try:
        task = PostTask.objects.get(id=pk)

        if task.job_status == "Completed":
            return Response({"detail": "Not Found"}, status=404)
        proposal = task.proposals.all().select_related('user', 'user__profile').order_by('created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 4
        paginator_qs = paginator.paginate_queryset(proposal, request)
        proposal_serializer = ProposalSerializer(paginator_qs, many=True)

        serializer = TasksSerializer(task, many=False, context={"request": request})
        context = {
            "task": serializer.data,
            "proposals": proposal_serializer.data,
        }
        return paginator.get_paginated_response(context)
        # return Response(proposals, status=200)
    except PostTask.DoesNotExist:
        return Response({"detail": "Not Found"}, status=404)


class FreelancersListApiView(generics.ListAPIView):
    pagination_class = GeneralPaginationClass
    serializer_class = ProfileSerializer
    queryset = Profile.objects.filter(updated=True).select_related('user').order_by('created_at')

    def get_queryset(self):
        sortBy = self.request.query_params.get("sortBy", None)
        search = self.request.query_params.get("search", None)
        rate = self.request.query_params.get("rate", None)
        skills = self.request.query_params.getlist("skills", None)
        queryset = self.queryset
        if sortBy:
            if sortBy == "oldest":
                queryset = queryset.order_by('created_at')
            elif sortBy == "newest":
                queryset = queryset.order_by('-created_at')
        if search:
            queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search))
        if rate:
            rate = rate.split(',')
            queryset = queryset.filter(Q(rate__gte=rate[0]) & Q(rate__lte=rate[1]))
        if skills:
            queryset = queryset.filter(reduce(operator.or_, (Q(skills__icontains=x) for x in skills)))
        return queryset


@api_view(['GET'])
def freelancer_profile(request, pk, *args, **kwargs):
    try:
        profile = Profile.objects.get(id=pk)
        if not profile.updated:
            return Response({"detail": "Not found."}, status=404)

        ip = request.META['REMOTE_ADDR']
        if request.user != profile.user:
            if (request.user.is_authenticated and not HitCount.objects.filter(
                    Q(profile=profile) & Q(user=request.user)).exists()) or (
                    not request.user.is_authenticated and not (
                    HitCount.objects.filter(Q(profile=profile) & Q(ip=ip)).exists())):

                view = HitCount.objects.create(profile=profile)
                if request.user.is_authenticated:
                    view.user = request.user
                else:
                    view.ip = ip
                view.save()

        work_history = profile.user.proposals.filter(Q(status__exact='completed') & Q(rating__gt=0)) \
            .select_related('task').order_by('created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 4
        paginator_qs = paginator.paginate_queryset(work_history, request)
        work_history_serializer = WorkHistoryProposalSerializer(paginator_qs, many=True)

        serializer = ProfileSerializer(profile, many=False, context={"request": request})
        context = {
            "profile": serializer.data,
            "work_history": work_history_serializer.data,
        }
        return paginator.get_paginated_response(context)

    except Profile.DoesNotExist:
        return Response({"detail": "Not Found"}, status=404)


class BookmarkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TaskBookmarkSerializer
    pagination_class = GeneralPaginationClass

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.user.is_Employer:
            serializer_class = ProfileBookmarkSerializer
        return serializer_class

    def get_queryset(self):
        if self.request.user.is_Freelancer:
            ids = self.request.user.bookmarks.all().values_list('task', flat=True).order_by('-created_at')
            return PostTask.objects.filter(id__in=ids).order_by('-bookmark__created_at')
        if self.request.user.is_Employer:
            ids = self.request.user.bookmarks.all().values_list("freelancer_profile", flat=True).order_by('-created_at')
            return Profile.objects.filter(id__in=ids).order_by('-bookmark__created_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def bookmarked_view(request, *args, **kwargs):
    serializer = BookmarkedSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if request.user.is_Freelancer:
        task = get_object_or_404(PostTask, pk=serializer.validated_data.get("id"))
        bookmarks = request.user.bookmarks.filter(task=task)
        if bookmarks.exists():
            bookmarks.delete()
            return Response({"detail": "Removed"}, status=200)
        else:
            bookmark_task = Bookmark.objects.create(user=request.user, task=task)
            bookmark_task.save()
            return Response({"detail": "Bookmarked"}, status=200)
    elif request.user.is_Employer:
        profile = get_object_or_404(Profile, pk=serializer.validated_data.get("id"))
        bookmarks = request.user.bookmarks.filter(freelancer_profile=profile)
        if bookmarks.exists():
            bookmarks.delete()
            return Response({"detail": "Removed"}, status=200)
        else:
            bookmark_profile = Bookmark.objects.create(user=request.user, freelancer_profile=profile)
            bookmark_profile.save()
            return Response({"detail": "Bookmarked"}, status=200)


class DeactivateAccountView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.profileImg.delete()
        if instance.is_Freelancer:
            instance.profile.userCV.delete()
        self.perform_destroy(instance)
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
