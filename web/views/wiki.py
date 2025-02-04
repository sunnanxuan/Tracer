from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from web.forms.wiki import WikiModelForm
from django.views.decorators.csrf import csrf_exempt
from utils.AWS_S3.S3_bucket import upload_file_to_s3
from utils.encrypt import uid




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
    print(form)
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







@csrf_exempt
def wiki_upload(request, project_id):
    result={
        'success': 0,
        'message': None,
        'url': None
    }
    image_object = request.FILES.get('editormd-image-file')
    print(request.FILES)
    if not image_object:
        result['message']='文件不存在'
        return JsonResponse(result)
    ext=image_object.name.split('.')[-1]
    key="{}.{}".format(uid(request.tracer.user.mobile_phone),ext)
    image_url=upload_file_to_s3(request.tracer.project.bucket,image_object,key)
    result['success']=1
    result['message'] = '上传文件成功'
    result['url']=image_url
    return JsonResponse(result)



