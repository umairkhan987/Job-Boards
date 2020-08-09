from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, Http404
from django.shortcuts import render

from accounts.models import Profile, User
from employer.models import PostTask
from hireo.models import Bookmark


def index(request):
    return render(request, 'Hireo/index.html')


def messages(request):
    return render(request, 'Hireo/messages.html')


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
            # set order_by(created_at) of bookmarks then it print multiple time
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
