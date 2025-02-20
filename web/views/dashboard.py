import time
from datetime import datetime
from django.shortcuts import render,redirect,HttpResponse
import time
import collections
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from web import models





def dashboard(request,project_id):
    status_dict=collections.OrderedDict()
    for key, text in models.Issues.status_choices:
        status_dict[key]={'text':text, 'count':0}
    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] =item['ct']

    user_list=models.ProjectUser.objects.filter(project_id=project_id).values('user_id','user__username')

    top_ten=models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[:10]

    context = {
        'status_dict':status_dict,
        'top_ten_object':top_ten,
        'user_list':user_list
    }
    return render(request,'dashboard.html',context)





def issues_chart(request, project_id):
    today = timezone.now().date()
    date_dict = collections.OrderedDict()
    # 构造最近 30 天的数据，每天生成毫秒级时间戳
    for i in range(30):
        date = today - timedelta(days=i)
        # 将 date 转换为 datetime 对象
        dt = datetime.combine(date, datetime.min.time())
        date_dict[date.strftime('%Y-%m-%d')] = [int(dt.timestamp() * 1000), 0]

    result = models.Issues.objects.filter(
        project_id=project_id,
        create_datetime__gte=today - timedelta(days=30)
    ).extra(
        select={'ctime': "strftime('%%Y-%%m-%%d', web_issues.create_datetime)"}
    ).values('ctime').annotate(ct=Count('id'))

    for item in result:
        if item['ctime'] in date_dict:
            date_dict[item['ctime']][1] = item['ct']

    # 将数据反转为从最早到最新排序
    data = list(reversed(date_dict.values()))
    return JsonResponse({'status': True, 'data': data})
