from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from web.forms.wiki import WikiModelForm




def wiki(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    return render(request, 'wiki.html')




def wiki_add(request, project_id):
    if request.method == 'GET':
        form=WikiModelForm(request)
        return render(request, 'wiki_add.html', {'form': form})
    form=WikiModelForm(request, data=request.POST)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project=request.tracer.project
        form.save()
        url=reverse('wiki', kwargs={'project_id':project_id})
        return redirect(url)
    return render(request, 'wiki_add.html', {'form': form})



def wiki_catalog(request, project_id):
    data=models.Wiki.objects.filter(project=request.tracer.project).values('id','title','parent_id').order_by('depth','id')
    return JsonResponse({'status':True,'data':list(data)})