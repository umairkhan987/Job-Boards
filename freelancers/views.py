from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect

from accounts.decorators import freelancer_required
from employer.models import PostTask
from .forms import ProposalForm
from .models import Proposal


def findTasks(request):
    tasks = PostTask.objects.all().order_by('-updated_at')
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
            return JsonResponse({"success": True, "msg": "Your bid has been submitted."})
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
def delete_proposal(request, id):
    try:
        proposal = get_object_or_404(Proposal, pk=id)
        if proposal.user != request.user:
            raise Http404("You are not permitted to perform this action.")

        if request.method == "POST" and request.is_ajax():
            proposal.delete()
            return JsonResponse({"success": True, "msg": "Proposal successfully deleted."})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
