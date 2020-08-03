from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F

from accounts.decorators import employer_required, valid_user_for_task
from accounts.models import Profile
from .forms import TaskForm
from .models import PostTask


def findFreelancer(request):
    try:
        if 'sortBy' in request.GET:
            print(request.GET)

        if request.GET is not None and len(request.GET).__gt__(1):
            print(request.GET)

        freelancers = Profile.objects.filter(created_at__lt=F('updated_at'))
        return render(request, "Employer/FindFreelancer.html", {"freelancers": freelancers})
    except Exception as e:
        raise Http404(str(e))


def freelancerProfile(request, id):
    profile = get_object_or_404(Profile, pk=id)
    return render(request, 'Employer/freelancerProfile.html', {"profile": profile})


@login_required
@employer_required
def postATask(request):
    form = TaskForm()
    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('my_tasks')
    return render(request, 'Employer/postATask.html', {"form": form})


@login_required
@employer_required
def myTasks(request):
    tasks = PostTask.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Employer/myTasks.html', {"tasks": tasks})


@login_required
@employer_required
@valid_user_for_task
def editTask(request, id):
    task = get_object_or_404(PostTask, pk=id)
    form = TaskForm(instance=task)
    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect('my_tasks')
    return render(request, 'Employer/postATask.html', {"form": form})


@login_required
@employer_required
@valid_user_for_task
def deleteTask(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            task = get_object_or_404(PostTask, pk=id)
            title = task.title
            task.task_file.delete()
            task.delete()
            return JsonResponse({"success": True, "msg": "" + title + " delete successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})