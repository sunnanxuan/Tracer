from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.issues import IssueModelForm, IssueReplyModelForm
from web import models
from django.shortcuts import get_object_or_404
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt




def issues(request, project_id):
    if request.method == 'GET':
        queryset = models.Issues.objects.filter(project_id=project_id).order_by('-create_datetime')
        page_object=Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=1
        )
        issues_list=queryset[page_object.start:page_object.end]
        form = IssueModelForm(request)
        context = {
            'issues_list': issues_list,
            'form': form,
            'page_html': page_object.page_html(),
        }
        return render(request, 'issues.html', context)

    form = IssueModelForm(request,data=request.POST)
    if form.is_valid():
        form.instance.project=request.tracer.project
        form.instance.creator=request.tracer.user
        form.save()
        return JsonResponse({'status':True})

    return JsonResponse({'status':False, 'error':form.errors})





def issues_detail(request, project_id,issues_id):
    issues_object=models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    form=IssueModelForm(request,instance=issues_object)
    return render(request,'issues_detail.html',{'issues_object':issues_object, 'form':form})




@csrf_exempt
def issues_record(request, project_id, issues_id):
    if request.method == 'GET':
        reply_list = models.IssueReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})

    form = IssueReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        # 根据 POST 数据设置父回复，如果存在，则设置 reply_id，否则保持为空
        parent_id = request.POST.get('reply')
        if parent_id and parent_id.strip():
            form.instance.reply_id = parent_id
        else:
            form.instance.reply = None
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


