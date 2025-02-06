from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web import models
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
    """
    创建新的 Wiki 文档
    """
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form': form})

    # 处理 POST 请求
    form = WikiModelForm(request, data=request.POST, files=request.FILES)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()  # 创建新文档
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    # 如果表单验证失败，返回表单页并显示错误信息
    return render(request, 'wiki_form.html', {'form': form})







def wiki_catalog(request, project_id):
    data=models.Wiki.objects.filter(project=request.tracer.project).values('id','title','parent_id').order_by('depth','id')
    return JsonResponse({'status':True,'data':list(data)})






def wiki_delete(request, project_id, wiki_id):
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    url = reverse('wiki', kwargs={'project_id':project_id})
    return redirect(url)



def wiki_edit(request, project_id, wiki_id):
    """
    编辑现有的 Wiki 文档
    """
    wiki_object = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        # 如果文档不存在，重定向到 Wiki 列表页
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    if request.method == 'GET':
        # 初始化表单，并传入当前文档的实例
        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form, 'wiki_object': wiki_object})

    # 处理 POST 请求
    form = WikiModelForm(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()  # 更新现有文档
        url = reverse('wiki', kwargs={'project_id': project_id})
        preview_url = f"{url}?wiki_id={wiki_id}"
        return redirect(preview_url)

    # 如果表单验证失败，返回表单页并显示错误信息
    return render(request, 'wiki_form.html', {'form': form, 'wiki_object': wiki_object})







@csrf_exempt
def wiki_upload(request, project_id):
    """
    处理 CKEditor 图片上传请求
    """
    result = {
        'success': 0,
        'message': None,
        'url': None
    }

    print(request.FILES)

    # CKEditor 的图片上传字段为 'upload'
    image_object = request.FILES.get('upload')
    if not image_object:
        result['message'] = '文件不存在'
        return JsonResponse(result)

    # 获取文件扩展名
    ext = image_object.name.split('.')[-1]
    # 生成唯一的文件名
    key = "{}.{}".format(uid(request.tracer.user.mobile_phone), ext)
    # 上传文件到 S3
    image_url = upload_file_to_s3(request.tracer.project.bucket, image_object, key)

    # 返回 CKEditor 需要的格式
    result['success'] = 1
    result['message'] = '上传文件成功'
    result['url'] = image_url
    return JsonResponse(result)


