import json
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render

from .decorators import freelancer_required
from .forms import CustomUserForm, UserForm, ProfileForm


def login(request):
    try:
        if request.method == "POST":
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                email = request.POST['username']
                password = request.POST['password']
                user = auth.authenticate(email=email, password=password)
                if user is not None:
                    auth_login(request, user)
                    return JsonResponse({'success': True, 'msg': "Successfully Login"})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                return JsonResponse({'success': False, 'errors': errors})
        # return render(request, 'registerForm.html', {'form': form})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


def register(request):
    try:
        if request.method == "POST":
            form = CustomUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                auth_login(request, user)
                return JsonResponse({'success': True, 'msg': "Successfully Register"})
            else:
                customError = dict()
                for (k, v) in form.errors.as_data().items():
                    customError[k] = [str(error)[1:-1][1:-1] for error in v]
                return JsonResponse({'success': False, 'errors': customError})
                # customErrors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
        # return render(request, 'registerForm.html', {'form': form})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
def settings(request):
    return render(request, 'Hireo/settings.html')


@login_required
def changePassword(request):
    try:
        if request.method == 'POST':
            form = PasswordChangeForm(data=request.POST, user=request.user)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                return JsonResponse({'success': True, 'msg': 'Password is Successfully updated.'})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                print(errors)
                return JsonResponse({'success': False, 'errors': errors})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
def updateAccount(request):
    try:
        if request.method == 'POST':
            form = UserForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True, 'msg': 'Successfully updated'})
            else:
                errors = form.errors.as_data()
                print(errors)
                return JsonResponse({'success': False, 'errors': "Some thing is happened."})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
@freelancer_required
def updateProfile(request):
    try:
        if request.method == "POST" and request.is_ajax():
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.save()
                return JsonResponse({'success': True, 'msg': 'Successfully updated'})
            else:
                errors = profile_form.errors.as_data()
                return JsonResponse({'success': False, 'errors': errors})
        elif not request.is_ajax():
            raise Http404("Invalid Request")
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
@freelancer_required
def getProfile(request):
    if request.method == "GET" and request.is_ajax():
        try:
            data = model_to_dict(request.user.profile)
            data.pop('user')
            filename = None
            if data.get('userCV'):
                file = data.pop('userCV')
                filename = json.dumps(str(file))

            return JsonResponse({'success': True, 'profile': data, "file": filename})
        except Exception as e:
            return JsonResponse({"success": False, "errors": str(e)})
    elif not request.is_ajax():
        raise Http404("Invalid request")
    else:
        return JsonResponse({'success': False, 'errors': "User is not valid"})
