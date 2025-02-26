from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
from utils.AWS_S3.S3_bucket import get_temporary_credentials
from web import models


def setting(request, project_id):
    project = request.tracer.project  # 当前项目对象
    if request.method == 'GET':
        return render(request, 'setting.html', {'project': project})

    if request.tracer.user!=request.tracer.project.creator:
        return render(request, 'setting_delete.html', {'error': "只有项目创建者可以修改项目"})


    # 判断提交的是哪一个表单，根据不同按钮名称判断
    if 'update_name' in request.POST:
        new_name = request.POST.get('project_name')
        if not new_name:
            error_name = "项目名称不能为空"
            return render(request, 'setting.html', {'project': project, 'error_name': error_name})
        project.name = new_name
        project.save()
        return redirect('setting', project_id=project.id)

    elif 'update_desc' in request.POST:
        new_desc = request.POST.get('project_desc')
        # 允许描述为空，也可以加非空判断
        project.desc = new_desc
        project.save()
        return redirect('setting', project_id=project.id)


    # 默认返回修改页面
    return render(request, 'setting.html', {'project': project})




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







def user_manage(request, project_id):
    participants = models.ProjectUser.objects.filter(project=request.tracer.project)
    return render(request, 'user_manage.html', {
        'participants': participants,
    })



def user_delete(request, project_id, participant_id):
    project = request.tracer.project
    # 检查当前用户是否为项目创建者
    if request.tracer.user != project.creator:
        return HttpResponse("只有项目创建者可以删除参与者", status=403)

    # 不允许删除项目创建者
    if int(participant_id) == project.creator.id:
        return HttpResponse("不能删除项目创建者", status=400)

    try:
        participant = models.ProjectUser.objects.get(project=project, user_id=participant_id)
    except models.ProjectUser.DoesNotExist:
        return HttpResponse("参与者不存在", status=404)

    participant.delete()
    return redirect('user_manage', project_id=project.id)
