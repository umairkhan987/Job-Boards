from django.db.models import F, Q
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.models import Profile
from employer.models import PostTask
from hireo.api.pagination import GeneralPaginationClass
from hireo.api.serializers import PostTaskSerializer, ProfileSerializer, ProposalSerializer, \
    WorkHistoryProposalSerializer


@api_view(['GET'])
def index(request):
    try:
        tasks = PostTask.objects.all()
        total_task = tasks.count()
        tasks = tasks.exclude(job_status__exact="Completed").order_by('-created_at')[:5]
        tasks_serializers = PostTaskSerializer(tasks, many=True)
        freelancers = Profile.objects.select_related('user').all()
        total_profile = freelancers.count()
        freelancers = freelancers.filter(created_at__lt=F('updated_at')).order_by('-rating')[:6]
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


class TaskListApiView(ListAPIView):
    pagination_class = GeneralPaginationClass
    serializer_class = PostTaskSerializer
    queryset = PostTask.objects.exclude(job_status__exact="Completed").order_by('-created_at')

    def get_queryset(self):
        sortBy = self.request.query_params.get("sortBy", None)
        search = self.request.query_params.get("search", None)
        rate = self.request.query_params.get("rate", None)
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
        # TODO: skills_list query_parameter needed
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

        serializer = PostTaskSerializer(task, many=False, context={"request": request})
        context = {
            "task": serializer.data,
            "proposals": proposal_serializer.data,
        }
        return paginator.get_paginated_response(context)
        # return Response(proposals, status=200)
    except PostTask.DoesNotExist:
        return Response({"detail": "Not Found"}, status=404)


class FreelancersListApiView(ListAPIView):
    pagination_class = GeneralPaginationClass
    serializer_class = ProfileSerializer
    queryset = Profile.objects.filter(created_at__lt=F('updated_at')).select_related('user').order_by('created_at')

    def get_queryset(self):
        sortBy = self.request.query_params.get("sortBy", None)
        search = self.request.query_params.get("search", None)
        rate = self.request.query_params.get("rate", None)
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
        # TODO: skills_list query_parameter needed
        return queryset


@api_view(['GET'])
def freelancer_profile(request, pk, *args, **kwargs):
    try:
        profile = Profile.objects.get(id=pk)
        # TODO: Hit_count logic remaining

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
