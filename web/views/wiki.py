from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from web.forms.wiki import WikiModelForm




def wiki(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')
    wiki_object=models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'wiki.html', {'wiki_object':wiki_object})




def wiki_add(request, project_id):
    if request.method == 'GET':
        form=WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form': form})
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
    return render(request, 'wiki_form.html', {'form': form})



def wiki_catalog(request, project_id):
    data=models.Wiki.objects.filter(project=request.tracer.project).values('id','title','parent_id').order_by('depth','id')
    return JsonResponse({'status':True,'data':list(data)})




def wiki_delete(request, project_id, wiki_id):
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    url = reverse('wiki', kwargs={'project_id':project_id})
    return redirect(url)



def wiki_edit(request, project_id, wiki_id):
    wiki_object=models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id':project_id})
        return redirect(url)
    if request.method == 'GET':
        form=WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form})
    form=WikiModelForm(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        url=reverse('wiki', kwargs={'project_id':project_id})
        preview_url = f"{url}?wiki_id={wiki_id}"
        return redirect(preview_url)
    return render(request, 'wiki_form.html', {'form': form})