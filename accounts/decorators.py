from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.shortcuts import get_object_or_404

from employer.models import PostTask
from freelancers.models import Proposal


def freelancer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='index'):
    """
    decorator to check that logged in user is freelancers
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_Freelancer,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def employer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="index"):
    """
    decorator to check that logged in user is employer
    """

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_Employer,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def valid_user_for_task(view_func):
    """ This decorator is used to prevent user to edit or delete another user task """
    def wrap(request, *args, **kwargs):
        id = kwargs['id']
        task = get_object_or_404(PostTask, pk=id)

        if request.user == task.user:
            return view_func(request, *args, **kwargs)
        else:
            raise Http404("You are not permitted to perform this action.")
    return wrap


def valid_user_for_proposal(view_func):
    """ This decorator is used to prevent user to edit or delete another user task """
    def wrap(request, *args, **kwargs):
        id = kwargs['id']
        proposal = get_object_or_404(Proposal, pk=id)
        if not proposal:
            raise Http404("Your proposal not found.")

        if request.user == proposal.user:
            return view_func(request, *args, **kwargs)
        else:
            raise Http404("You are not permitted to perform this action.")
    return wrap

