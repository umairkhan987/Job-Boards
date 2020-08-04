from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect

from accounts.decorators import freelancer_required, valid_user_for_proposal
from employer.models import PostTask
from .forms import ProposalForm
from .models import Proposal


def findTasks(request):
    task_lists = PostTask.objects.all().order_by('-created_at')
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
    return render(request, 'Freelancer/ViewTask.html', {"task": task})


@login_required
@freelancer_required
def submit_proposals(request):
    try:
        if request.method == "POST" and request.is_ajax():
            form = ProposalForm(request.POST)
            if form.is_valid():
                task = PostTask.objects.get(pk=request.POST['task_id'])
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
    try:
        proposals = Proposal.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'Freelancer/MyProposals.html', {"proposals": proposals})
    except Exception as e:
        raise Http404(str(e))


@login_required
@freelancer_required
@valid_user_for_proposal
def delete_proposal(request, id):
    try:
        if request.method == "POST" and request.is_ajax():
            proposal = get_object_or_404(Proposal, pk=id)

            if proposal.accept:
                return JsonResponse({"success": False, "errors": "You are not permitted to delete this Proposal"})

            proposal.delete()
            return JsonResponse({"success": True, "msg": "Proposal successfully deleted."})
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
            proposal.user.profile.total_job_done -= 1
            proposal.accept = False

            proposal.task.save()
            proposal.user.profile.save()
            proposal.save()
            return JsonResponse({"success": True, "msg": "Job cancelled."})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})