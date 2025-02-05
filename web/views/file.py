from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from web import models
from django.urls import reverse
from web.forms.file import FolderModelForm
from django.views.decorators.csrf import csrf_exempt
from utils.AWS_S3.S3_bucket import upload_file_to_s3, delete_file_from_s3, delete_file_list_from_s3, \
    get_temporary_credentials
from utils.encrypt import uid
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_POST
import uuid
import boto3
from botocore.exceptions import ClientError


def file(request, project_id):
    parent_object = None

    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracer.project).first()

    if request.method == 'GET':

        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent

        queryset = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form = FolderModelForm(request, parent_object)
        context = {'form': form,
                   'parent_object': parent_object,
                   'file_object_list': file_object_list,
                   'breadcrumb_list': breadcrumb_list}
        return render(request, 'file.html', context)

    print(request.POST)
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2,
                                                           project=request.tracer.project).first()
    if edit_object:
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        form = FolderModelForm(request, parent_object, data=request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.instance.update_datetime = timezone.now()
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def file_delete(request, project_id):
    fid = request.GET.get('fid')
    delete_object = models.FileRepository.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        request.tracer.project.use_space -= delete_object.file_size
        request.tracer.project.save()
        delete_file_from_s3(request.tracer.project.bucket, delete_object.key)
        delete_object.delete()
        return JsonResponse({'status': True})

    total_size = 0
    key_list = []

    folder_list = [delete_object, ]
    for folder in folder_list:
        child_list = models.FileRepository.objects.filter(parent=folder, project=request.tracer.project).order_by(
            '-file_type')
        for child in child_list:
            if child.file_type == 2:
                folder_list.append(child)
            else:
                total_size += child.file_size
                key_list.append(child.key)

    if key_list:
        delete_file_list_from_s3(request.tracer.project.bucket, key_list)

    if total_size:
        request.tracer.project.use_space -= total_size
        request.tracer.project.save()

    delete_object.delete()
    return JsonResponse({'status': True})





@require_POST
def upload_file(request, project_id):
    # 获取所有上传的文件（前端 input 标签的 name 为 uploadFile）
    file_objs = request.FILES.getlist('uploadFile')
    if not file_objs:
        return JsonResponse({'status': False, 'error': '未上传任何文件'})

    # 查找当前用户最新有效的订单（状态为已支付），从中获取收费策略
    transaction = models.Transaction.objects.filter(
        user=request.tracer.user,
        status=2  # 已支付
    ).order_by('-create_datetime').first()

    # 这里直接认为 transaction 一定存在，如果可能为空，可增加判断返回错误
    file_size_limit_bytes = transaction.price_policy.project_file_size * 1024 * 1024
    project_space_limit_bytes = transaction.price_policy.project_space * 1024 * 1024
    single_file_limit = transaction.price_policy.project_file_size

    total_upload_size = 0
    # 校验每个文件大小是否超限，并累计上传总大小
    for file_obj in file_objs:
        if file_obj.size > file_size_limit_bytes:
            return JsonResponse({
                'status': False,
                'error': f"文件 '{file_obj.name}' 大小超过限制，当前限制为 {single_file_limit} M"
            })
        total_upload_size += file_obj.size

    # 校验上传后项目总使用空间是否超过允许的空间
    project = request.tracer.project
    if project.use_space + total_upload_size > project_space_limit_bytes:
        available_space_mb = round((project_space_limit_bytes - project.use_space) / (1024 * 1024), 2)
        return JsonResponse({
            'status': False,
            'error': f"项目空间不足，剩余空间仅有 {available_space_mb} M"
        })

    # 获取当前文件夹的 ID（前端可通过隐藏域或 query string 传入）
    folder_id = request.POST.get('folder', '').strip()
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(
            id=int(folder_id),
            file_type=2,  # 确保是文件夹
            project=project  # 确保属于当前项目
        ).first()
    else:
        parent_object = None  # 若无有效 folder_id，则放在根目录

    bucket_name = project.bucket

    # 获取临时凭证
    credentials = get_temporary_credentials()
    if not credentials:
        return JsonResponse({'status': False, 'error': '获取临时凭证失败'})

    # 使用临时凭证创建 S3 客户端
    s3_client = boto3.client(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=settings.AWS_DEFAULT_REGION,
    )

    file_urls = []  # 用于存放上传成功的文件 URL 列表

    # 循环处理每个上传的文件（此时已通过总大小校验，所以可以安全上传所有文件）
    for file_obj in file_objs:
        # 生成一个唯一的 S3 key，保证文件在 S3 中不重复
        ext = file_obj.name.split('.')[-1] if '.' in file_obj.name else ''
        unique_key = uuid.uuid4().hex
        if ext:
            unique_key = f"{unique_key}.{ext}"

        try:
            # 上传文件到 S3，使用生成的 unique_key 作为 S3 对象 key
            s3_client.upload_fileobj(file_obj, bucket_name, unique_key)
        except ClientError as e:
            print(f"Error uploading file {file_obj.name}: {e}")
            return JsonResponse({'status': False, 'error': f"上传文件 {file_obj.name} 失败: {str(e)}"})

        # 构造文件访问 URL（不同区域格式可能不同）
        region = settings.AWS_DEFAULT_REGION
        if region == 'us-east-1':
            file_url = f"https://{bucket_name}.s3.amazonaws.com/{unique_key}"
        else:
            file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_key}"

        # 保存文件记录到数据库
        new_file = models.FileRepository(
            project=project,
            file_type=1,  # 文件
            name=file_obj.name,
            key=unique_key,
            file_size=file_obj.size,
            file_path=file_url,
            parent=parent_object,
            update_user=request.tracer.user,
            update_datetime=timezone.now(),
        )
        new_file.save()

        file_urls.append(file_url)

    # 上传成功后，更新项目已使用空间
    project.use_space += total_upload_size
    project.save()

    return JsonResponse({'status': True, 'file_urls': file_urls})

