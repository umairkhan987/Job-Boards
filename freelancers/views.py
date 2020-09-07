import operator
from calendar import month_abbr, month_name
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from accounts.decorators import freelancer_required, valid_user_for_proposal
from employer.models import PostTask
from hireo.models import Offers, HitCount
from .forms import ProposalForm
from .models import Proposal


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
        if request.method == "POST" and not request.is_ajax():
            raise Http404("Invalid request.")
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@freelancer_required
def my_proposals(request):
    sort = request.GET.get("sort-by", None)

    proposal_list = Proposal.objects.filter(user=request.user).exclude(task_id=None)
    if sort != 'pending' and sort != "relevance" and sort:
        proposal_list = proposal_list.filter(status__iexact=sort)
    elif sort == "pending":
        proposal_list = proposal_list.filter(status__isnull=True)
    else:
        proposal_list = proposal_list.order_by('-created_at')

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
            return JsonResponse({"success": True, "delete": True, "msg": "Proposal successfully deleted."})
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
            return JsonResponse({"success": True, "msg": "Job cancelled."})
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
            return JsonResponse({"success": True, "msg": "Job Completed."})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
@freelancer_required
def dashboard(request):
    views = HitCount.objects.filter(profile=request.user.profile)
    month = request.user.profile.created_at.month
    data = [views.filter(created_at__month=((month + x) % 12) or 12).count() or '' for x in range(6)]
    labels = [month_name[((month + i) % 12) or 12] for i in range(6)]
    context = {
        "labels": labels,
        "data": data
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
                return JsonResponse({"success": True, "msg": "Offer Deleted"})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        raise Http404(str(e))
