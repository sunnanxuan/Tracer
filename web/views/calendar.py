from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from web.models import Issues


def calendar_page(request):
    return render(request, 'calendar.html')


def calendar_events(request):
    events = []
    # 获取指派给当前用户且截止时间不为空的问题
    assigned_issues = Issues.objects.filter(assign=request.tracer.user, end_datetime__isnull=False)
    for issue in assigned_issues:
        events.append({
            'title': f"截止: {issue.subject}",
            'start': issue.end_datetime.isoformat(),
            'color': '#ff5722'
        })
    # 可扩展其他事件……
    return JsonResponse(events, safe=False)
