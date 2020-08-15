from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Max, QuerySet
from django.forms import model_to_dict
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import Profile, User
from employer.models import PostTask
from hireo.forms import MessageForm, OfferForm
from hireo.models import Bookmark, Messages


def index(request):
    return render(request, 'Hireo/index.html')


@login_required
def messages(request):
    if request.method == "POST" and request.is_ajax():
        form = MessageForm(request.POST)
        if form.is_valid():
            receiver_id = request.POST.get('receiver_id')
            receiver = User.objects.get(pk=receiver_id)
            message = form.save(commit=False)
            message.receiver = receiver
            message.sender = request.user
            message.save()
            return JsonResponse({"success": True, "msg": "Message Sent"})
        else:
            errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
            return JsonResponse({'success': False, 'errors': errors})
    else:
        message_list = get_current_user_msg(request)
        return render(request, 'Hireo/messages.html', {"messages": message_list})


@login_required
def message_details(request, id):
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
        from (  select *, first_value(created_at)
        over (partition by min(receiver_id, sender_id), max(receiver_id, sender_id) order by created_at desc ) last_date
        from hireo_messages
        where %s in (receiver_id, sender_id) )
        where created_at = last_date order by id desc
        """, [request.user.id])
