from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models
from django.shortcuts import get_object_or_404





def dashboard(request,project_id):
    project = get_object_or_404(models.Project, id=project_id)

    # 使用 project 进行逻辑处理
    return render(request, 'dashboard.html', {'project': project})



def issues(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    # 使用 project_id 进行逻辑处理
    return render(request, 'issues.html', {'project': project})



def statistics(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    # 使用 project_id 进行逻辑处理
    return render(request, 'statistics.html', {'project': project})





