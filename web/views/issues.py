from dataclasses import field

from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.issues import IssueModelForm, IssueReplyModelForm
from web import models
import json
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





@csrf_exempt
def issues_change(request, project_id, issues_id):
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    if not issues_object:
        return JsonResponse({'status': False, 'error': '问题不存在'})
    post_dict = json.loads(request.body.decode('utf-8'))
    name = post_dict.get('name')
    if not name:
        return JsonResponse({'status': False, 'error': '缺少字段名称'})
    try:
        field_object = models.Issues._meta.get_field(name)
    except Exception as e:
        return JsonResponse({'status': False, 'error': f'字段 {name} 不存在'})
    value = post_dict.get('value')

    def change_reply_record(content):
        new_object = models.IssueReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=content,
            creator=request.tracer.user,
        )
        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_id': new_object.reply_id
        }
        return new_reply_dict

    if name in ['subject', 'desc', 'start_datetime', 'end_datetime']:
        if not value:
            if name == 'subject' and (not value or not value.strip()):
                return JsonResponse({'status': False, 'error': '问题标题不能为空'})
            if not field_object.null:
                return JsonResponse({'status': False, 'error': '您选择的值不能为空'})
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = '{}更新为空'.format(field_object.verbose_name)
        else:
            # 修正：将传入的 value 正确赋值给对应字段
            setattr(issues_object, name, value)
            issues_object.save()
            change_record = '{}更新为{}'.format(field_object.verbose_name, value)
        return JsonResponse({'status': True, 'data': change_reply_record(change_record)})

    # 以下部分处理其他字段，保持不变
    if name in ['issues_type', 'module', 'assign', 'parent']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': '您的选择不能为空'})
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = '{}更新为空'.format(field_object.verbose_name)
        else:
            if name == 'assign':
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id, user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': '您选择的值不存在'})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = '{}更新为{}'.format(field_object.verbose_name, str(instance))
            else:
                instance = field_object.remote_field.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': '您选择的值不存在'})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = '{}更新为{}'.format(field_object.verbose_name, str(instance))
        return JsonResponse({'status': True, 'data': change_reply_record(change_record)})

    if name in ['priority', 'status', 'mode']:
        selected_text = None
        for key, text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': '您选择的值不存在'})
        setattr(issues_object, name, value)
        issues_object.save()
        change_record = '{}更新为{}'.format(field_object.verbose_name, selected_text)
        return JsonResponse({'status': True, 'data': change_reply_record(change_record)})

    if name == 'attention':
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': '数据格式错误'})
        if not value:
            issues_object.attention.set(value)
            issues_object.save()
            change_record = '{}更新为空'.format(field_object.verbose_name)
        else:
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': '用户名不存在请重新设置'})
                username_list.append(username)
            issues_object.attention.set(value)
            issues_object.save()
            change_record = '{}更新为{}'.format(field_object.verbose_name, ",".join(username_list))
        return JsonResponse({'status': True, 'data': change_reply_record(change_record)})








