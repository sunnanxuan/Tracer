from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from django.http import JsonResponse
import boto3
from botocore.exceptions import ClientError
from utils.AWS_S3.S3_bucket import get_temporary_credentials
from web import models
from django.shortcuts import render, get_object_or_404
from web.forms.account import ChangeEmailForm, ChangePasswordForm, ChangeUsernameForm, ChangeMobilePhoneForm


def homepage(request):
    return render(request, 'homepage.html')



def change_username(request):
    if request.method == 'GET':
        form = ChangeUsernameForm()
        return render(request, 'change_username.html', {'form': form})
    else:
        form = ChangeUsernameForm(data=request.POST, instance=request.tracer.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, 'data': '/users/homepage/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})



def change_email(request):
    if request.method == 'GET':
        form = ChangeEmailForm()
        return render(request, 'change_email.html', {'form': form})
    else:
        form = ChangeEmailForm(data=request.POST, instance=request.tracer.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, 'data': '/users/homepage/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})



def change_mobile_phone(request):
    if request.method == 'GET':
        form = ChangeMobilePhoneForm()
        return render(request, 'change_mobile_phone.html', {'form': form})
    else:
        form = ChangeMobilePhoneForm(data=request.POST, instance=request.tracer.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, 'data': '/users/homepage/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})




def change_password(request):
    if request.method == 'GET':
        form = ChangePasswordForm()
        return render(request, 'change_password.html', {'form': form})
    else:
        form = ChangePasswordForm(data=request.POST, instance=request.tracer.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, 'data': '/users/homepage/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})






