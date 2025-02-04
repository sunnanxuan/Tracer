from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web import models
from django.urls import reverse
from web.forms.file import FolderModelForm
from django.views.decorators.csrf import csrf_exempt
from utils.AWS_S3.S3_bucket import upload_file_to_s3
from utils.encrypt import uid


def file(request, project_id):
    parent_object=None
    folder_id=request.GET.get('folder_id', '')
    if folder_id.isdecimal():
        parent_object=models.FileRepository.objects.filter(id=int(folder_id),file_type=2,
                                                           project=request.tracer.project).first()

    if request.method=='GET':
        queryset=models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            file_object_list=queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form=FolderModelForm(request,parent_object)
        return render(request,'file.html', {'form':form,'parent_object':parent_object,'file_object_list':file_object_list})

    form=FolderModelForm(request,parent_object, data=request.POST)
    if form.is_valid():
        form.instance.project=request.tracer.project
        form.instance.file_type=2
        form.instance.update_user=request.tracer.user
        form.instance.parent=parent_object
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'error': form.errors})




