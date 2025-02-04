from os.path import exists

from django import forms

from web import models
from web.forms.bootstrap import BootStrapForm
from web.models import FileRepository
from django.core.exceptions import ValidationError


class FolderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ['name']

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_object = parent_object
        self.request = request

    def clean_name(self):
        name = self.cleaned_data['name']
        queryset = FileRepository.objects.filter(file_type=2,name=name, project=self.request.tracer.project)

        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists=queryset.filter(parent__isnull=True).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return name


