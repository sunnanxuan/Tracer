from lib2to3.fixes.fix_input import context

from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from requests import delete

from web import models
from django.urls import reverse
from web.forms.file import FolderModelForm
from django.views.decorators.csrf import csrf_exempt
from utils.AWS_S3.S3_bucket import upload_file_to_s3,delete_file_from_s3, delete_file_list_from_s3,extract_key_from_s3_url
from utils.encrypt import uid
from django.utils import timezone


def file(request, project_id):
    parent_object=None
    folder_id=request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object=models.FileRepository.objects.filter(id=int(folder_id),file_type=2,
                                                           project=request.tracer.project).first()

    if request.method=='GET':

        breadcrumb_list=[]
        parent=parent_object
        while parent:
            breadcrumb_list.insert(0,{'id':parent.id,'name':parent.name})
            parent=parent.parent

        queryset=models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            file_object_list=queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form=FolderModelForm(request,parent_object)
        context={'form':form,
                 'parent_object':parent_object,
                 'file_object_list':file_object_list,
                 'breadcrumb_list':breadcrumb_list}
        return render(request,'file.html', context)

    fid=request.POST.get('fid', '')
    edit_object=None
    if fid.isdecimal():
        edit_object=models.FileRepository.objects.filter(id=int(fid),file_type=2,
                                                         project=request.tracer.project).first()
    if edit_object:
        form=FolderModelForm(request,parent_object, data=request.POST, instance=edit_object)
    else:
        form=FolderModelForm(request,parent_object, data=request.POST)

    if form.is_valid():
        form.instance.project=request.tracer.project
        form.instance.file_type=2
        form.instance.update_user=request.tracer.user
        form.instance.parent=parent_object
        form.instance.update_datetime = timezone.now()
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'error': form.errors})




def file_delete(request, project_id):
    fid=request.GET.get('fid')
    delete_object=models.FileRepository.objects.filter(id=fid,project=request.tracer.project).first()
    if delete_object.file_type == 1:
        request.tracer.project.use_space-=delete_object.file_size
        request.tracer.project.save()
        delete_file_from_s3(request.tracer.project.bucket, extract_key_from_s3_url(delete_object.key))
        delete_object.delete()
        return JsonResponse({'status': True})

    total_size=0
    key_list=[]

    folder_list=[delete_object,]
    for folder in folder_list:
        child_list=models.FileRepository.objects.filter(parent=folder,project=request.tracer.project).order_by('-file_type')
        for child in child_list:
            if child.file_type==2:
                folder_list.append(child)
            else:
                total_size+=child.file_size
                key_list.append(extract_key_from_s3_url(child.key))

    if key_list:
        delete_file_list_from_s3(request.tracer.project.bucket, key_list)

    if total_size:
        request.tracer.project.use_space-=total_size
        request.tracer.project.save()

    delete_object.delete()
    return JsonResponse({'status':True})




