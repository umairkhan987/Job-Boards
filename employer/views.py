from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from accounts.decorators import employer_required, valid_user_for_task
from accounts.models import User, Profile
from freelancers.models import Proposal
from .forms import TaskForm, OfferForm
from .models import PostTask
from notification.models import Notification, notification_handler


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
    sort = request.GET.get("sort-by", None)
    task_list = PostTask.objects.filter(user=request.user).order_by('-created_at')
    if sort and sort != "relevance":
        task_list = task_list.filter(job_status__iexact=sort)

    page = request.GET.get('page', 1)
    paginator = Paginator(task_list, 4)

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
            html = None
            if not request.user.tasks.exists():
                msg = "There are no tasks"
                html = render_to_string("common/partial_empty_msg.html", {"msg": msg})
            return JsonResponse({"success": True, "msg": "" + title + " delete successfully", "html": html})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@employer_required
@valid_user_for_task
def manage_proposal(request, id):
    sort = request.GET.get("sort-by")

    task = PostTask.objects.get(pk=id)
    page = request.GET.get("page", 1)
    proposal_list = task.proposals.all()

    if sort == "HF":
        proposal_list = proposal_list.order_by("-rate")
    elif sort == "LF":
        proposal_list = proposal_list.order_by("rate")
    else:
        proposal_list = proposal_list.order_by("created_at")

    paginator = Paginator(proposal_list, 3)

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
            proposal.status = "accepted"

            proposal.user.profile.save()
            proposal.task.save()
            proposal.save()
            notification_handler(request.user, proposal.user, Notification.ACCEPT_OFFER, target=proposal)
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

    # notifications
    notifications_list = request.user.notifications.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications_list, 5)

    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    if request.is_ajax():
        html = render_to_string("Notification/include/partial_dashboard_notifications_list.html",
                                {"notifications": notifications})
        return JsonResponse({"success": True, "html": html})

    return render(request, 'Employer/Dashboard.html', {"data": data, "notifications": notifications})


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
    try:
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
            notification_handler(request.user, proposal.user, Notification.POST_REVIEW, target=proposal.task)
            return JsonResponse({"success": True, 'msg': "Review submitted"})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        raise Http404(str(e))


@login_required
@employer_required
def send_offers(request):
    try:
        if request.method == "POST" and request.is_ajax():
            form = OfferForm(request.POST, request.FILES)
            id = request.POST.get("profile_id")
            email = request.POST.get("email")
            if form.is_valid():
                profile = get_object_or_404(Profile, pk=id)
                sender = User.objects.filter(email=email).first()
                offer = form.save(commit=False)
                offer.sender = sender if sender is not None else None
                offer.profile = profile
                offer.save()
                return JsonResponse({"success": True, "msg": "Offer send"})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                return JsonResponse({"success": False, "errors": errors})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        raise Http404(str(e))
