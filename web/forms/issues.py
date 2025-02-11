from PIL.Image import module
from django import forms
from web.forms.bootstrap import BootStrapForm
from web import models


class IssueModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model=models.Issues
        exclude=['project', 'creator', 'create_datetime','lastest_datetime']
        widgets = {
            "module": forms.Select(attrs={'class':'selectpicker', "data-live-search":'true'}),
            "parent": forms.Select(attrs={'class': 'selectpicker', "data-live-search": 'true'}),
            "issues_type": forms.Select(attrs={'class': 'selectpicker', "data-live-search": 'true'}),
            "assign": forms.Select(attrs={'class': 'selectpicker', "data-live-search": 'true'}),
            "attention": forms.SelectMultiple(attrs={'class': 'selectpicker', "data-live-search": 'true', "data-actions-box":"true"}),

        }

    def __init__(self, request, *args, **kwargs):
        super().__init__( *args, **kwargs)

        self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=request.tracer.project).values_list('id','title')

        module_list=[('',"没有选中任何项"),]
        module_object_list=models.Module.objects.filter(project=request.tracer.project).values_list('id','title')
        module_list.extend(module_object_list)
        self.fields['module'].choices = module_list

        total_user_list=[(request.tracer.project.creator_id,request.tracer.project.creator.username),]
        project_user_list=models.ProjectUser.objects.filter(project=request.tracer.project).values_list('user_id','user__username')
        total_user_list.extend(project_user_list)
        self.fields['assign'].choices = [('',"没有选中任何项")]+total_user_list
        self.fields['attention'].choices = total_user_list

        parent_list=[('',"没有选中任何项"),]
        parent_object_list=models.Issues.objects.filter(project=request.tracer.project).values_list('id','subject')
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices = parent_list




class IssueReplyModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model=models.IssueReply
        fields = ['content']
