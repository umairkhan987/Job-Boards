import operator
from functools import reduce

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from accounts.models import Profile, User
from employer.models import PostTask
from notification.models import MessageNotification
from .forms import MessageForm, OfferForm
from .models import Bookmark, Messages, HitCount


def index(request):
    return render(request, 'Hireo/index.html', {})


def findTasks(request):
    task_lists = PostTask.objects.all().exclude(job_status__exact="Completed").order_by('-created_at')

    if request.GET:
        search = request.GET.get('search', None)
        rate = request.GET.get('rate', None)
        skill_list = request.GET.getlist('skills', None)

        if search:
            task_lists = task_lists.filter(title__icontains=search)

        if rate:
            rate = rate.split(',')
            task_lists = task_lists.filter(Q(min_price__gte=rate[0]) & Q(max_price__lte=rate[1]))

        if skill_list:
            task_lists = task_lists.filter(reduce(operator.or_, (Q(skills__icontains=x) for x in skill_list)))

    if request.GET.get("sortBy"):
        sort = request.GET.get("sortBy", None)
        if sort == "newest":
            task_lists = task_lists.order_by("-created_at")
        elif sort == "oldest":
            task_lists = task_lists.order_by("created_at")

    page = request.GET.get('page', 1)

    paginator = Paginator(task_lists, 5)
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    return render(request, 'Freelancer/FindTasks.html', {"tasks": tasks})


def view_task(request, id):
    task = get_object_or_404(PostTask, pk=id)
    proposals = task.proposals.all().select_related('user').order_by('created_at')
    page = request.GET.get("page", 1)
    paginator = Paginator(proposals, 4)

    try:
        proposals = paginator.page(page)
    except PageNotAnInteger:
        proposals = paginator.page(1)
    except EmptyPage:
        proposals = paginator.page(paginator.num_pages)

    proposals_list = render_to_string('Freelancer/includes/partial_proposals_list.html', {"proposals": proposals})
    if request.is_ajax():
        return JsonResponse({"success": True, "html_proposal_list": proposals_list})

    return render(request, 'Freelancer/ViewTask.html', {"task": task, "proposals": proposals})


def find_freelancer(request):
    freelancer_list = Profile.objects.filter(created_at__lt=F('updated_at')).order_by('created_at')
    if request.GET:
        search = request.GET.get('search', None)
        rate = request.GET.get('rate', None)
        skill_list = request.GET.getlist('skills', None)
        if search:
            freelancer_list = freelancer_list.filter(
                Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search))

        if rate:
            rate = rate.split(',')
            freelancer_list = freelancer_list.filter(Q(rate__gte=rate[0]) & Q(rate__lte=rate[1]))

        if skill_list:
            freelancer_list = freelancer_list.filter(reduce(operator.or_, (Q(skills__icontains=x) for x in skill_list)))

    if request.GET.get("sortBy"):
        sort = request.GET.get("sortBy", None)
        if sort == "newest":
            freelancer_list = freelancer_list.order_by("-created_at")
        elif sort == "oldest":
            freelancer_list = freelancer_list.order_by("created_at")

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
    profile = get_object_or_404(Profile, pk=id)
    session = request.session.session_key
    ip = request.META['REMOTE_ADDR']

    if (request.user.is_authenticated and not HitCount.objects.filter(
            Q(profile=profile) & Q(user=request.user)).exists()) or (
            not request.user.is_authenticated and not (
            HitCount.objects.filter(Q(profile=profile) & Q(ip=ip)).exists())):

        view = HitCount.objects.create(profile=profile)
        if request.user.is_authenticated:
            view.user = request.user
            view.session = session
        else:
            view.ip = ip
        view.save()

    work_history_list = profile.user.proposals.select_related('task').filter(status__exact='completed').order_by(
        'created_at')
    page = request.GET.get("page", 1)
    paginator = Paginator(work_history_list, 4)

    try:
        work_history = paginator.page(page)
    except PageNotAnInteger:
        work_history = paginator.page(1)
    except EmptyPage:
        work_history = paginator.page(paginator.num_pages)

    context = {
        "profile": profile,
        "work_history": work_history
    }
    return render(request, 'Employer/freelancerProfile.html', context)


@login_required
def messages(request):
    try:
        if request.method == "POST" and request.is_ajax():
            form = MessageForm(request.POST)
            if form.is_valid():
                receiver_id = request.POST.get('receiver_id')
                receiver = User.objects.get(pk=receiver_id)
                message = form.save(commit=False)
                message.receiver = receiver
                message.sender = request.user
                message.save()
                current_message = render_to_string("Hireo/includes/partial_message.html", {"message": message})
                return JsonResponse({"success": True, "msg": "Message Sent", "current_message": current_message})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                return JsonResponse({'success': False, 'errors': errors})
        else:
            message_list = get_current_user_msg(request)
            return render(request, 'Hireo/messages.html', {"messages": message_list})
    except Exception as e:
        raise Http404(str(e))


@login_required
def message_details(request, id):
    notifications = MessageNotification.objects.filter(actor_id=id, recipient_id=request.user.id)
    if notifications.exists():
        notifications.update(is_read=True)

    message_list = get_current_user_msg(request)
    receiver = User.objects.get(pk=id)
    full_name = receiver.first_name + " " + receiver.last_name
    message_detail = []
    if receiver:
        message_detail = Messages.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)).order_by(
            'created_at')

    context = {
        "full_name": full_name,
        "messages": message_list,
        "message_details": message_detail,
    }
    return render(request, 'Hireo/messages.html', context)


@login_required
def messages_delete(request):
    try:
        if request.method == "POST" and request.is_ajax():
            id = request.POST.get("receiver_id")
            receiver = User.objects.get(pk=id)
            conversation = Messages.objects.filter(
                Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
            if conversation.exists():
                conversation.delete()
                # TODO: update query and find alternative way to delete messages.
                # conversation.filter(sender=request.user).update(sender=None)
                # conversation.filter(receiver=request.user).update(receiver=None)
                return JsonResponse({"success": True, "msg": "Conversation Deleted.", "url": redirect("messages").url})
            else:
                return JsonResponse({"success": False, "errors": "Conversation not found."})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        raise Http404(str(e))


@login_required
def bookmarks(request):
    if request.method == "POST" and request.is_ajax():
        user = User.objects.get(email=request.user.email)
        id = request.POST.get('id')

        # check if its task or user
        task = None
        profile = None
        try:
            if user.is_Employer:
                profile = Profile.objects.get(pk=id)
            elif user.is_Freelancer:
                task = PostTask.objects.get(pk=id)
        except Exception as e:
            raise Http404(str(e))

        # check if user is employer and and if already bookmarked then delete it.
        if user.is_Employer:
            if request.user.bookmarks.filter(freelancer_profile=profile).exists():
                Bookmark.objects.filter(user=request.user, freelancer_profile=profile).delete()
                return JsonResponse({"success": True, "msg": "Removed"})

        # check if user is freelancer and and if already bookmarked then delete it.
        if user.is_Freelancer:
            if request.user.bookmarks.filter(task=task).exists():
                Bookmark.objects.filter(user=request.user, task=task).delete()
                return JsonResponse({"success": True, "msg": "Removed"})

        bookmark = Bookmark.objects.create(user=user)
        if user.is_Employer:
            bookmark.freelancer_profile = profile
        elif user.is_Freelancer:
            bookmark.task = task
        bookmark.save()
        return JsonResponse({"success": True, "msg": "Bookmarked"})

    else:
        bookmark_list = []
        if request.user.is_Employer:
            ids = request.user.bookmarks.all().values_list("freelancer_profile", flat=True).order_by('-created_at')
            bookmark_list = User.objects.filter(profile__in=ids).order_by('-profile__bookmark__created_at')

        if request.user.is_Freelancer:
            ids = request.user.bookmarks.all().values_list('task', flat=True).order_by('-created_at')
            bookmark_list = PostTask.objects.filter(id__in=ids).order_by('-bookmark__created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(bookmark_list, 5)

        try:
            bookmark_list = paginator.page(page)
        except PageNotAnInteger:
            bookmark_list = paginator.page(1)
        except EmptyPage:
            bookmark_list = paginator.page(paginator.num_pages)

    return render(request, 'Hireo/bookmarks.html', {"bookmarks": bookmark_list})


@login_required
def deactivate_account(request):
    try:
        if request.method == "POST" and request.is_ajax():
            user = User.objects.get(email=request.user.email)
            logout(request)
            user.profileImg.delete()  # delete user image
            user.profile.userCV.delete()  # delete user profile CV
            user.delete()
            return JsonResponse({"success": True, 'msg': "User Deactivated", 'url': redirect('index').url})
        elif request.method == "POST" and not request.is_ajax():
            raise Http404("Invalid Request")

    except Exception as e:
        raise Http404(str(e))


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
    except Exception as e:
        raise Http404(str(e))


# TODO: convert this query into django queryset
def get_current_user_msg(request):
    return Messages.objects.raw(
        """
        select id, receiver_id, sender_id, message_content, created_at
        from (  select *, max(created_at)
        over (partition by min(receiver_id, sender_id), max(receiver_id, sender_id)) last_date
        from hireo_messages
        where %s in (receiver_id, sender_id) )
        where created_at = last_date order by id desc
        """, [request.user.id])
