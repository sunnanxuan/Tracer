from os.path import exists

from django import forms
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web import models
from web.forms.widgets import ColorRadioSelect

class ProjectModelForm(BootStrapForm, forms.ModelForm):
    bootstrap_class_exclude=['color']
    class Meta:
        model = models.Project
        fields = ['name','color','desc']
        widgets = {
            'desc': forms.Textarea,
            'color':ColorRadioSelect(attrs={'class':'color-radio'}),
        }


    def __init__(self,requset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requset=requset

    def clean_name(self):
        name = self.cleaned_data['name']
        exists=models.Project.objects.filter(name=name, creator=self.requset.tracer.user).exists()
        if exists:
            raise ValidationError('项目已存在')
        count = models.Project.objects.filter(creator=self.requset.tracer.user).count()
        if count > self.requset.tracer.price_policy.project_num:
            raise ValidationError('项目个数超限，请购买套餐')
        return name