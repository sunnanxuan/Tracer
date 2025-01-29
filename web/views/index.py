from django.shortcuts import render, redirect,HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm
from django.core.exceptions import ValidationError




def index(request):
    return render(request, 'index.html')