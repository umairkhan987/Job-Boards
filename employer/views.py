from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F

from accounts.decorators import employer_required, valid_user_for_task
from accounts.models import Profile, User
from freelancers.models import Proposal
from .forms import TaskForm
from .models import PostTask


def find_freelancer(request):
    freelancer_list = Profile.objects.filter(created_at__lt=F('updated_at')).order_by('created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(freelancer_list, 5)

    try:
        freelancers = paginator.page(page)
    except PageNotAnInteger:
        freelancers = paginator.page(1)
    except EmptyPage:
        freelancers = paginator.page(paginator.num_pages)

    return render(request, "Employer/FindFreelancer.html", {"freelancers": freelancers})


def freelancer_profile(request, id):
    session = request.session.session_key
    ip = request.META['REMOTE_ADDR']

    print("Session ", session)
    print("IP ", ip)

    profile = get_object_or_404(Profile, pk=id)
    return render(request, 'Employer/freelancerProfile.html', {"profile": profile})


@login_required
@employer_required
def post_a_task(request):
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
def my_tasks(request):
    # TODO: order by based on list of string [In progress, Pending, Completed]
    task_list = PostTask.objects.filter(user=request.user).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(task_list, 3)

    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    return render(request, 'Employer/myTasks.html', {"tasks": tasks})


@login_required
@employer_required
@valid_user_for_task
def edit_task(request, id):
    task = get_object_or_404(PostTask, pk=id)
    if task.job_status == "In Progress":
        raise Http404(
            "You can't perform this action because task is in progress."
            " If you change requirement send direct message to user.")

    form = TaskForm(instance=task)
    if request.method == "POST":
        task_obj = PostTask.objects.get(pk=id)
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            if form.files and task_obj.task_file:
                task_obj.task_file.delete()

            form.save()
            return redirect('my_tasks')
    return render(request, 'Employer/postATask.html', {"form": form})


@login_required
@employer_required
@valid_user_for_task
def delete_task(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            task = get_object_or_404(PostTask, pk=id)
            if task.job_status == "In Progress" or task.job_status == "Completed":
                return JsonResponse({"success": False,
                                     "errors":
                                         "Your are not permitted to perform this action. Only Pending task will be delete."
                                     })

            title = task.title
            task.task_file.delete()
            task.delete()
            return JsonResponse({"success": True, "msg": "" + title + " delete successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@employer_required
@valid_user_for_task
def manage_proposal(request, id):
    task = PostTask.objects.get(pk=id)
    page = request.GET.get("page", 1)
    paginator = Paginator(task.proposals.all().order_by('created_at'), 5)

    try:
        proposals = paginator.page(page)
    except PageNotAnInteger:
        proposals = paginator.page(1)
    except EmptyPage:
        proposals = paginator.page(paginator.num_pages)

    return render(request, 'Employer/ManageProposal.html', {"task": task, "proposals": proposals})


@login_required
@employer_required
def accept_proposal(request, id):
    try:
        proposal = get_object_or_404(Proposal, pk=id)
        if not proposal and request.is_ajax():
            return JsonResponse({"success": False, "errors": "Proposal not found."})
        if proposal.task.user != request.user and request.is_ajax():
            return JsonResponse({"success": False, "errors": "You are not permitted to perform this action."})

        task = proposal.task
        if task.proposals.filter(status='accepted').exists() and request.is_ajax():
            return JsonResponse({"success": False, "errors": "Sorry your are not assign this job to multiple user."})
        if task.proposals.filter(status='completed').exists() and request.is_ajax():
            return JsonResponse({"success": False, "errors": "Your job is completed"})

        if request.method == "POST" and request.is_ajax():
            proposal.user.profile.total_hired += 1
            proposal.task.job_status = 'In Progress'
            proposal.proposal_accept_date = timezone.now()
            proposal.status = "accepted"

            proposal.user.profile.save()
            proposal.task.save()
            proposal.save()
            return JsonResponse({"success": True, "msg": "Proposal accepted.", "url": redirect('my_tasks').url})

        if request.method == "POST" and not request.is_ajax():
            raise Http404("Invalid request.")
    except Exception as e:
        raise Http404(str(e))


@login_required
@employer_required
def dashboard(request):
    user = User.objects.get(email=request.user.email)
    pending = user.tasks.filter(job_status__exact="Pending").count()
    total_Proposals = Proposal.objects.filter(task__in=request.user.tasks.all()).count()
    data = [user.tasks.count(), user.task_completed(), user.task_InProgress(), pending, total_Proposals, 0]
    return render(request, 'Employer/Dashboard.html', {"data": data})


@login_required
@employer_required
def reviews(request):
    proposal_list = Proposal.objects.filter(
        task__in=request.user.tasks.filter(job_status__exact="Completed"),
        status__exact='completed').order_by('-updated_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(proposal_list, 3)

    try:
        proposals = paginator.page(page)
    except PageNotAnInteger:
        proposals = paginator.page(1)
    except EmptyPage:
        proposals = paginator.page(paginator.num_pages)

    return render(request, 'Employer/Reviews.html', {"proposals": proposals})


@login_required
@employer_required
def post_reviews(request, id):
    if request.method == "POST" and request.is_ajax():
        proposal = get_object_or_404(Proposal, pk=id)
        if not request.user.tasks.filter(proposals=proposal).exists():
            return JsonResponse({"success": False, 'errors': "You are not permitted to perform this action."})

        budget = request.POST.get('onBudget')
        time = request.POST.get('onTime')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        proposal.onBudget = True if budget == "yes" else False
        proposal.onTime = True if time == "yes" else False
        proposal.rating = rating
        proposal.comment = comment
        proposal.save()
        return JsonResponse({"success": True, 'msg': "Review submitted"})
    else:
        raise Http404("Invalid request")
