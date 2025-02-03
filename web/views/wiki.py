from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from web.forms.wiki import WikiModelForm




def wiki(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    # 使用 project_id 进行逻辑处理
    return render(request, 'wiki.html', {'project': project})




def wiki_add(request, project_id):
    if request.method == 'GET':
        form=WikiModelForm(request)
        return render(request, 'wiki_add.html', {'form': form})
    form=WikiModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project=request.tracer.project
        form.save()
        url=reverse('wiki', kwargs={'project_id':project_id})
        return redirect(url)
    return render(request, 'wiki_add.html', {'form': form})