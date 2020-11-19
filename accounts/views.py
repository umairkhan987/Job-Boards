import json
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse, Http404
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render
from django.template.loader import render_to_string

from .decorators import freelancer_required
from .forms import CustomUserForm, UserForm, ProfileForm
from .models import Profile, User


def login(request):
    try:
        if request.method == "POST" and request.is_ajax():
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
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
def settings(request):
    form = UserForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    context = {
        'form': form,
        "password_form": password_form,
        "profile_form": profile_form,
    }
    return render(request, 'Hireo/settings.html', context)


@login_required
def changePassword(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            form = PasswordChangeForm(data=request.POST, user=request.user)
            success = False
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                success = True
                # errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
            html = render_to_string('Hireo/include/partial_password_change_setting.html', {"password_form": form},
                                    request=request)
            return JsonResponse({'success': success, "html": html, 'msg': 'Password is Successfully updated.'})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
def updateAccount(request):
    try:
        if request.method == 'POST' and request.is_ajax():
            user = User.objects.get(email=request.user.email)
            success = False
            form = UserForm(request.POST, request.FILES, instance=request.user)

            if form.is_valid():
                if form.files and user.profileImg:
                    user.profileImg.delete()
                form.save()
                success = True

            html = render_to_string("Hireo/include/partial_account_setting.html", {"form": form}, request=request)
            return JsonResponse({'success': success, 'html': html, "msg": "Successfully updated"})

    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
@freelancer_required
def updateProfile(request):
    try:
        if request.method == "POST" and request.is_ajax():
            usercv = request.POST.get("userCV", None)
            profile = Profile.objects.get(user=request.user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

            success = False
            if profile_form.is_valid():

                # replace old cv with new one
                if profile_form.files and profile.userCV:
                    profile.userCV.delete()

                #     delete file when user delete the file
                if usercv == "null":
                    profile.userCV.delete()
                    profile_form.instance.userCV.delete()

                profile_form.save()
                success = True
                # return JsonResponse({'success': True, 'msg': 'Successfully updated'})
                #     errors = profile_form.errors.as_data()
            html = render_to_string('Hireo/include/partial_profile_setting.html', {"profile_form": profile_form},
                                    request=request)
            return JsonResponse({'success': success, 'html': html, 'msg': 'Successfully updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})


@login_required
@freelancer_required
def getProfile(request):
    if request.method == "GET" and request.is_ajax():
        try:
            data = model_to_dict(request.user.profile)
            print("data ", data)

            data.pop('user')
            filename = None
            if data.get('userCV'):
                file = data.pop('userCV')
                filename = json.dumps(str(file))
            else:
                data.pop('userCV')

            return JsonResponse({'success': True, 'profile': data, "file": filename})
        except Exception as e:
            return JsonResponse({"success": False, "errors": str(e)})
    elif not request.is_ajax():
        raise Http404("Invalid request")
    else:
        return JsonResponse({'success': False, 'errors': "User is not valid"})
