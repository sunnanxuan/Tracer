from lib2to3.fixes.fix_input import context

from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web import models
from django.urls import reverse
from web.forms.file import FolderModelForm
from django.views.decorators.csrf import csrf_exempt
from utils.AWS_S3.S3_bucket import upload_file_to_s3
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
        # 如果是文件，可能执行相应逻辑
        pass
    else:
        # 如果是文件夹，执行相应逻辑
        pass
    delete_object.delete()
    return JsonResponse({'status':True})




