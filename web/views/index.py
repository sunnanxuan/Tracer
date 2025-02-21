from django.shortcuts import render, redirect,HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm
from django.core.exceptions import ValidationError
from web import models




def index(request):
    return render(request, 'index.html')




def document(request):
    return render(request, 'document.html')


def information(request):
    return render(request, 'information.html')





def price_policy(request):
    policies = models.PricePolicy.objects.all().order_by('category', 'price')
    return render(request, 'price_policy.html', {'policies': policies})
