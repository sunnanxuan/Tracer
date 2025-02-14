from dataclasses import field
from os.path import exists

from PIL.ImagePalette import random
from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.issues import IssueModelForm, IssueReplyModelForm,InviteModelForm
from web import models
import json
from utils.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from utils.uid import uid





class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 获取当前 URL 中该筛选项的所有值
            value_list = self.request.GET.getlist(self.name)
            # 为了不影响原始的 value_list，这里复制一份用于生成新的 URL 参数
            new_value_list = value_list.copy()
            if key in value_list:
                ck = 'checked'
                # 如果已经选中，则移除这个 key，实现取消选中
                new_value_list.remove(key)
            else:
                # 如果未选中，则添加该 key，实现选中
                new_value_list.append(key)
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, new_value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            url = "{}?{}".format(self.request.path_info, query_dict.urlencode())
            tpl = "<a class='cell' href='{url}'><input type='checkbox' {ck} /><label>{text}</label></a>"
            html = tpl.format(ck=ck, text=text, url=url)
            yield mark_safe(html)




class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe('<select class="select2" multiple="multiple" style="width: 100%;">')
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            # 每次都复制一份 GET 参数列表，避免修改原始列表
            orig_value_list = self.request.GET.getlist(self.name)
            new_value_list = orig_value_list.copy()
            if key in orig_value_list:
                selected = 'selected'
                new_value_list.remove(key)
            else:
                new_value_list.append(key)
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, new_value_list)
            if 'page' in query_dict:
                query_dict.pop('page')
            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)
            else:
                url = self.request.path_info
            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, text=text, selected=selected)
            yield mark_safe(html)
        yield mark_safe('</select>')






def issues(request, project_id):
    if request.method == 'GET':
        allow_filter_name=['issues_type','status','priority']
        condition={}
        for name in allow_filter_name:
            value_list=request.GET.getlist(name)
            if not value_list:
                continue
            condition["{}__in".format(name)]=value_list

        queryset = models.Issues.objects.filter(project_id=project_id, **condition).order_by('-create_datetime')
        page_object=Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=3
        )
        issues_list=queryset[page_object.start:page_object.end]
        form = IssueModelForm(request)
        project_issues_ytpe=models.IssuesType.objects.filter(project_id=project_id).values_list('id','title')
        project_total_user=[(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
        join_user=models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id','user__username')
        project_total_user.extend(join_user)
        invite_form=InviteModelForm()
        context = {
            'issues_list': issues_list,
            'form': form,
            'page_html': page_object.page_html(),
            'invite_form': invite_form,
            'filter_list':[
                {'title':'问题类型', 'filter':CheckFilter('issues_type',project_issues_ytpe,request)},
                {'title': '状态', 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': '优先级', 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': '指派者', 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': '关注者', 'filter': SelectFilter('attention', project_total_user, request)},
            ]
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






def invite_url(request,project_id):
    form=InviteModelForm(data=request.POST)
    if form.is_valid():
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period','无权创建邀请码')
            return JsonResponse({'status': False,'error':form.errors})

        random_invite_code=uid(request.tracer.user.mobile_phone)
        form.instance.project=request.tracer.project
        form.instance.code=random_invite_code
        form.instance.creator=request.tracer.user
        form.save()

        url = "{scheme}://{host}/{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': random_invite_code}),
        )

        return JsonResponse({'status': True, 'data': url})
    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'invite_join.html', {'error': '邀请码不存在'})
    if invite_object.project.creator == request.tracer.user:
        return render(request, 'invite_join.html', {'error': '创建者无需再加入项目'})
    exists = models.ProjectUser.objects.filter(project=invite_object.project, user=request.tracer.user).exists()
    if exists:
        return render(request, 'invite_join.html', {'error': '已加入项目无需再加入项目'})

    print(request.tracer.price_policy)
    max_member = request.tracer.price_policy.project_member
    current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    current_member = current_member + 1
    if current_member > max_member:
        return render(request, 'invite_join.html', {'error': '项目成员超限，请升级套餐'})

    current_datetime = timezone.now()
    limit_datetime = invite_object.create_datetime + timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})

    if invite_object.count:
        if invite_object.use_count >= invite_object.count:
            return render(request, 'invite_join.html', {'error': '邀请码数据已使用完'})
    invite_object.use_count += 1
    invite_object.save()
    models.ProjectUser.objects.create(user=request.tracer.user, project=invite_object.project)
    return render(request, 'invite_join.html', {'project': invite_object.project})








