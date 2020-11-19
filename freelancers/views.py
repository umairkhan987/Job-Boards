from calendar import month_name

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from accounts.decorators import freelancer_required, valid_user_for_proposal
from employer.models import PostTask
from hireo.models import HitCount
from .forms import ProposalForm
from .models import Proposal
from employer.models import Offers
from notification.models import Notification, notification_handler


@login_required
@freelancer_required
def submit_proposals(request):
    try:
        if request.method == "POST" and request.is_ajax():
            task = PostTask.objects.get(pk=request.POST['task_id'])
            if task.proposals.filter(user=request.user).exists():
                return JsonResponse({"success": False, "errors": "You bid has already been submitted."})

            form = ProposalForm(request.POST)
            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.user = request.user
                proposal.task = task
                proposal.save()
                return JsonResponse(
                    {"success": True, "msg": "Your bid has been submitted.", "url": redirect('my_proposals').url})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                return JsonResponse({'success': False, 'errors': errors})

        else:
            raise Http404("Invalid request.")
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@freelancer_required
def my_proposals(request):
    sort = request.GET.get("sort-by", None)

    proposal_list = Proposal.objects.filter(user=request.user).select_related("task").exclude(task_id=None).order_by(
        '-updated_at')
    if sort != 'pending' and sort != "relevance" and sort:
        proposal_list = proposal_list.filter(status__iexact=sort)
    elif sort == "pending":
        proposal_list = proposal_list.filter(status__isnull=True)
    else:
        order = ['accepted', None, 'completed', 'cancelled']
        order = {key: i for i, key in enumerate(order)}
        proposal_list = sorted(proposal_list, key=lambda proposal: order.get(proposal.status, 0))
        # proposal_list = proposal_list.order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(proposal_list, 4)

    try:
        proposals = paginator.page(page)
    except PageNotAnInteger:
        proposals = paginator.page(1)
    except EmptyPage:
        proposals = paginator.page(paginator.num_pages)
    return render(request, 'Freelancer/MyProposals.html', {"proposals": proposals})


@login_required
@freelancer_required
@valid_user_for_proposal
def delete_proposal(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            proposal = get_object_or_404(Proposal, pk=id)

            if proposal.status is not None:
                return JsonResponse(
                    {"success": False, "errors": "You are not permitted to delete this Proposal"})

            proposal.delete()
            html = None
            if not request.user.proposals.exclude(task_id=None).exists():
                msg = "Currently you have not placed any bid yet."
                html = render_to_string("common/partial_empty_msg.html", {"msg": msg})
            return JsonResponse(
                {"success": True, "deleted": True, "html": html, "msg": "Proposal successfully deleted."})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@freelancer_required
@valid_user_for_proposal
def cancel_task(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            proposal = get_object_or_404(Proposal, pk=id)
            proposal.task.job_status = "Pending"
            proposal.status = "cancelled"

            proposal.task.save()
            proposal.user.profile.save()
            proposal.save()

            # calculate success rate and overall profile rating
            user = request.user
            user.profile.success_rate = user.profile.calculate_success_rate()
            user.profile.rating = user.profile.calculate_rating()
            user.profile.save()

            notification_handler(request.user, proposal.task.user, Notification.TASK_CANCELLED, target=proposal.task)
            return JsonResponse({"success": True, "msg": "Job cancelled."})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@freelancer_required
@valid_user_for_proposal
def task_completed(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            proposal = get_object_or_404(Proposal, pk=id)
            proposal.task.job_status = 'Completed'
            proposal.user.profile.total_job_done += 1
            proposal.status = 'completed'

            proposal.task.save()
            proposal.user.profile.save()
            proposal.save()

            # calculate success rate and overall profile rating
            user = request.user
            user.profile.success_rate = user.profile.calculate_success_rate()
            user.profile.rating = user.profile.calculate_rating()
            user.profile.save()

            notification_handler(request.user, proposal.task.user, Notification.TASK_COMPLETED, target=proposal.task)
            return JsonResponse({"success": True, "msg": "Job Completed."})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@freelancer_required
def dashboard(request):
    views = HitCount.objects.filter(profile=request.user.profile)
    month = request.user.profile.created_at.month
    data = [views.filter(created_at__month=((month + x) % 12) or 12).count() or '' for x in range(6)]
    labels = [month_name[((month + i) % 12) or 12] for i in range(6)]

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

    context = {
        "labels": labels,
        "data": data,
        "notifications": notifications
    }
    render_to_string('Freelancer/includes/partial_views_chart.html', context)

    return render(request, 'Freelancer/Dashboard.html', context)


@login_required
@freelancer_required
def offers(request):
    offer_list = Offers.objects.filter(profile=request.user.profile).order_by('-created_at')
    page = request.GET.get('page', None)
    paginator = Paginator(offer_list, 4)
    try:
        offer_list = paginator.page(page)
    except PageNotAnInteger:
        offer_list = paginator.page(1)
    except EmptyPage:
        offer_list = paginator.page(paginator.num_pages)

    return render(request, 'Freelancer/Offers.html', {"offers": offer_list})


@login_required
@freelancer_required
def delete_offer(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            offer = Offers.objects.get(id=id)
            if offer:
                if offer.profile != request.user.profile:
                    return JsonResponse(
                        {"success": False, "errors": "You are not permitted to perform this operation."})
                offer.delete()
                html = None
                if not request.user.profile.offers.exists():
                    msg = "There is no offers."
                    html = render_to_string("common/partial_empty_msg.html", {"msg": msg})
                return JsonResponse({"success": True, "msg": "Offer Deleted", "html": html})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        raise Http404(str(e))


@login_required
@freelancer_required
def reviews(request):
    proposal_list = Proposal.objects.filter(Q(user=request.user) & Q(task__isnull=False)).order_by("-updated_at")
    if proposal_list.exists():
        proposal_list = proposal_list.filter(Q(status__iexact="completed") & ~Q(rating=0.0))

    page = request.GET.get('page', 1)
    paginator = Paginator(proposal_list, 3)

    try:
        proposals = paginator.page(page)
    except PageNotAnInteger:
        proposals = paginator.page(1)
    except EmptyPage:
        proposals = paginator.page(paginator.num_pages)

    return render(request, 'Freelancer/Reviews.html', {"proposals": proposals})
