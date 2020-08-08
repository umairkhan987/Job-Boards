from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render

from accounts.models import User
from hireo.models import Bookmark


def index(request):
    return render(request, 'Hireo/index.html')


def messages(request):
    return render(request, 'Hireo/messages.html')


def bookmarks(request):
    if request.method == "POST" and request.is_ajax():
        user = User.objects.get(email=request.user.email)
        id = request.POST.get('id')

        if request.user.bookmarks.filter(freelancer_id=id).exists():
            Bookmark.objects.filter(user=request.user, freelancer_id=id).delete()
            return JsonResponse({"success": True, "msg": "Removed"})
        else:
            bookmark = Bookmark.objects.create(user=user)
            if user.is_Employer:
                bookmark.freelancer_id = id
            elif user.is_Freelancer:
                bookmark.task_id = id
            bookmark.save()

            return JsonResponse({"success": True, "msg": "Bookmarked"})
    else:
        ids = Bookmark.objects.all().values_list("freelancer_id", flat=True)
        bookmark_list = User.objects.filter(profile__in=ids)
        page = request.GET.get('page', 1)
        paginator = Paginator(bookmark_list, 5)

        try:
            bookmark_list = paginator.page(page)
        except PageNotAnInteger:
            bookmark_list = paginator.page(1)
        except EmptyPage:
            bookmark_list = paginator.page(paginator.num_pages)

    return render(request, 'Hireo/bookmarks.html', {"bookmarks": bookmark_list})
