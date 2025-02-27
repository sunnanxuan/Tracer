from django.shortcuts import render, redirect,HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm, LoginForm
from django.db.models import Q
from web import models
import uuid
from django.utils import timezone





def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html',{'form':form})
    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        instance=form.save()
        policy_object=models.PricePolicy.objects.filter(category=1,title='个人免费版').first()
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            user=instance,
            price_policy=policy_object,
            count=0,
            price=0,
            start_datetime=timezone.now(),
        )
        return JsonResponse({'status': True, 'data':'/login/sms/'})
    else:
        return JsonResponse({'status': False, 'error': form.errors})



def send_sms(request):
    form=SendSmsForm(request,data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})





def login_sms(request):
    if request.method == 'GET':
        form = LoginSmsForm()
        return render(request, 'login_sms.html',{'form':form})
    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        mobile_phone = form.cleaned_data['mobile_phone']
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id'] = user_object.id
        request.session.set_expiry(2592000)
        return JsonResponse({'status': True, 'data': '/index/'})
    else:
        return JsonResponse({'status': False, 'error': form.errors})



def login(request):
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'login.html', {'form':form})

    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user_object=models.UserInfo.objects.filter(Q(email=username) | Q(mobile_phone=username)).filter(password=password).first()

        if user_object:
            request.session['user_id'] = user_object.id
            request.session.set_expiry(2592000)
            return redirect('index')
        form.add_error('username', '用户名或密码错误')
    return render(request, 'login.html', {'form':form})




def image_code(request):
    from io import BytesIO
    from utils.image_code import check_code

    image_object, code=check_code()
    request.session['image_code']=code
    request.session.set_expiry(60)

    stream=BytesIO()
    image_object.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    request.session.flush()
    return redirect('index')


