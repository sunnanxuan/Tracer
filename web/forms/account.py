from cProfile import label
from os.path import exists
from tempfile import template

from django.conf import settings
from django.core.validators import RegexValidator
from django import forms
import random
from django_redis import get_redis_connection
from django.core.exceptions import ValidationError

from web import models
from utils.twilio.sms import send_sms_twilio
from utils import encrypt

from web.forms.bootstrap import BootStrapForm







class RegisterModelForm(BootStrapForm,forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(\+1)?[-\s.]?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}$', '手机号格式错误')]
    )
    password = forms.CharField(
        label='密码',
        max_length=64,
        min_length=8,
        error_messages={
            'min_length':'密码长度不能小于8个字符',
            'max_length':'密码长度不能大于64个字符'
        },
        widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        label='重复密码',
        max_length=64,
        min_length=8,
        error_messages={
            'min_length': '密码长度不能小于8个字符',
            'max_length': '密码长度不能大于64个字符'
        },
        widget=forms.PasswordInput()
    )
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )

    class Meta:
        model = models.UserInfo  # 确保 models.UserInfo 定义正确
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']


    def clean_username(self):
        username = self.cleaned_data['username']

        exists=models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists=models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return pwd


    def clean_confirm_password(self):
        pwd = self.cleaned_data['password']
        confirm_pwd = self.cleaned_data['confirm_password']
        if pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已注册')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        conn=get_redis_connection()
        redis_code=conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送验证码')
        redis_str_code=redis_code.decode('utf-8')
        if code.strip()!=redis_str_code:
            raise ValidationError('验证码错误请重新输入')
        return code



class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(\+1)?[-\s.]?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}$', '手机号格式错误')])

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        tpl=self.request.GET.get('tpl')
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError('手机号不存在')
        else:
            if exists:
                raise ValidationError('手机号已存在')

        code=random.randint(1000,9999)

        sms=send_sms_twilio(mobile_phone, code)
        if not sms:
            raise ValidationError('短信发送失败')

        conn=get_redis_connection()
        conn.set(mobile_phone,code,ex=60)

        return mobile_phone



class LoginSmsForm(BootStrapForm, forms.Form):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(\+1)?[-\s.]?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}$', '手机号格式错误')]
    )

    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        print(exists)
        if not exists:
            raise ValidationError('手机号不存在')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        conn=get_redis_connection()
        redis_code=conn.get(mobile_phone)

        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送验证码')
        redis_str_code=redis_code.decode('utf-8')
        if code.strip()!=redis_str_code:
            raise ValidationError('验证码错误请重新输入')
        return code




class LoginForm(BootStrapForm, forms.Form):
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return pwd

    def clean_code(self):
        code = self.cleaned_data['code']

        session_code=self.request.session.get('image_code')

        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')
        if code.strip().upper()!=session_code.upper():
            raise ValidationError('验证码输入错误')

        return code







class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['username']

    def clean_username(self):
        username = self.cleaned_data['username']

        exists=models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return username



class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email']
        exists=models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已使用')
        return email




class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(
        label='密码',
        max_length=64,
        min_length=8,
        error_messages={
            'min_length': '密码长度不能小于8个字符',
            'max_length': '密码长度不能大于64个字符'
        },
        widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        label='重复密码',
        max_length=64,
        min_length=8,
        error_messages={
            'min_length': '密码长度不能小于8个字符',
            'max_length': '密码长度不能大于64个字符'
        },
        widget=forms.PasswordInput()
    )

    class Meta:
        model = models.UserInfo
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return pwd


    def clean_confirm_password(self):
        pwd = self.cleaned_data['password']
        confirm_pwd = self.cleaned_data['confirm_password']
        if pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd



class ChangeMobilePhoneForm(forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(\+1)?[-\s.]?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}$', '手机号格式错误')]
    )
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )

    class Meta:
        model = models.UserInfo
        fields = ['mobile_phone']


    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已使用')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        conn=get_redis_connection()
        redis_code=conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送验证码')
        redis_str_code=redis_code.decode('utf-8')
        if code.strip()!=redis_str_code:
            raise ValidationError('验证码错误请重新输入')
        return code
