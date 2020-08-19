from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from accounts.decorators import freelancer_required, valid_user_for_proposal
from accounts.models import User
from employer.models import PostTask
from hireo.models import Offers
from .forms import ProposalForm
from .models import Proposal


def findTasks(request):
    task_lists = PostTask.objects.all().exclude(job_status__exact="Completed").order_by('-created_at')
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
    # TODO: order_by proposals base on list of strings.
    proposal_list = Proposal.objects.filter(user=request.user).exclude(task_id=None).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(proposal_list, 3)

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
            return JsonResponse({"success": True, "delete": True,  "msg": "Proposal successfully deleted."})
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
    return render(request, 'Freelancer/Dashboard.html', {})


@login_required
@freelancer_required
def offers(request):
    offer_list = Offers.objects.filter(profile=request.user.profile).order_by('-created_at')
    page = request.GET.get('page', None)
    paginator = Paginator(offer_list, 5)

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
