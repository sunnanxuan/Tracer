from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models
from django.shortcuts import get_object_or_404
import collections
from django.db.models import Count





def dashboard(request,project_id):
    status_dict=collections.OrderedDict()
    for key, text in models.Issues.status_choices:
        status_dict[key]={'text':text, 'count':0}
    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] =item['ct']

    user_list=models.ProjectUser.objects.filter(project_id=project_id).values('user_id','user__username')

    top_ten=models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[:10]

    context = {
        'status_dict':status_dict,
        'top_ten_object':top_ten,
        'user_list':user_list
    }
    return render(request,'dashboard.html',context)
