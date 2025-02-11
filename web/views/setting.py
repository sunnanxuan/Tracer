from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
from web import models
from utils.AWS_S3.S3_bucket import get_temporary_credentials  # 获取临时凭证的函数



def setting(request, project_id):
    return render(request, 'setting.html')



def setting_delete(request,project_id):
    if request.method == 'GET':
        return render(request, 'setting_delete.html')

    project_name=request.POST.get('project_name')

    if not project_name or project_name!=request.tracer.project.name:
        return render(request, 'setting_delete.html', {'error': "项目名错误"})

    if request.tracer.user!=request.tracer.project.creator:
        return render(request, 'setting_delete.html', {'error': "只有项目创建者可以删除项目"})

    models.Wiki.objects.filter(project=request.tracer.project).delete()

    models.FileRepository.objects.filter(project=request.tracer.project).delete()

    models.ProjectUser.objects.filter(project=request.tracer.project).delete()


    # 3. 删除对应的 S3 桶及其文件（如果存在）
    bucket_name = request.tracer.project.bucket
    if bucket_name:
        credentials = get_temporary_credentials()
        if credentials:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=settings.AWS_DEFAULT_REGION,
            )
            try:
                # 列出桶内的所有对象
                response = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in response:
                    # 构造要删除的对象列表
                    objects = [{'Key': obj['Key']} for obj in response['Contents']]
                    s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
            except ClientError as e:
                # 删除文件失败时记录日志，但不阻止后续操作
                print("删除桶中文件失败:", e)

            try:
                # 删除桶（要求桶为空）
                s3_client.delete_bucket(Bucket=bucket_name)
            except ClientError as e:
                print("删除桶失败:", e)
        else:
            print("获取临时凭证失败，无法删除 S3 桶")

    request.tracer.project.delete()

    return redirect('project_list')
