from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import Profile
from employer.models import PostTask
from hireo.api.serializers import PostTaskSerializer, ProfileSerializer


@api_view(['GET'])
def index(request):
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