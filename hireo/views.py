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
from .models import Bookmark, HitCount


def index(request):
    tasks = PostTask.objects.all()
    freelancers = Profile.objects.all()
    freelancers_profile = freelancers.filter(created_at__lt=F('updated_at'))
    sorted_freelancers = sorted(freelancers_profile, key=lambda a: a.calculate_rating(), reverse=True)

    context = {
        "total_tasks_posted": tasks.count(),
        "total_freelancers": freelancers.count(),
        "tasks": tasks.exclude(job_status__exact="Completed").order_by('-created_at')[:5],
        "freelancers": sorted_freelancers[:6]
    }
    return render(request, 'Hireo/index.html', context)


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

    html = render_to_string('Hireo/include/partial_proposals_list.html', {"proposals": proposals})
    if request.is_ajax():
        return JsonResponse({"success": True, "html": html})

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

    if request.user != profile.user:
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
                html = None
                if not request.user.bookmarks.exists():
                    msg = "There is no bookmark."
                    html = render_to_string("common/partial_empty_msg.html", {"msg": msg})
                return JsonResponse({"success": True, "msg": "Removed", "html": html})

        # check if user is freelancer and and if already bookmarked then delete it.
        if user.is_Freelancer:
            bookmark = request.user.bookmarks.filter(task=task)
            if bookmark.exists():
                bookmark.delete()
                html = None
                if not request.user.bookmarks.exists():
                    msg = "There is no bookmark."
                    html = render_to_string("common/partial_empty_msg.html", {"msg": msg})
                return JsonResponse({"success": True, "msg": "Removed", "html": html})

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
