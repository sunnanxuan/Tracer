
import json
from django.http import JsonResponse
from django.shortcuts import render
from web import models
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime, parse_date
import datetime
from django.utils import timezone




def calendar_page(request):
    return render(request, 'calendar.html')


def calendar_events(request):
    events = []
    manual_events = models.CalendarEvent.objects.filter(user=request.tracer.user)
    for ev in manual_events:
        if ev.type == '1':
            events.append({
                'title': ev.title,
                'start': ev.start.isoformat(),
                'color': '#FF6A6A'
            })
        else:
            events.append({
                'title': ev.title,
                'start': ev.start.isoformat(),
                'color': '#007aff'
            })
    return JsonResponse(events, safe=False)





@csrf_exempt
def add_calendar_event(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            title = data.get("title")
            time_str = data.get("time")  # 前端传来的时间字符串
            allDay = data.get("allDay", False)

            if not title or not time_str:
                return JsonResponse({'status': 'error', 'message': '缺少事件标题或时间'})

            # 如果是全天事件，解析为日期，并组合成当天午夜的 datetime 对象
            if allDay:
                dt_date = parse_date(time_str)
                if not dt_date:
                    return JsonResponse({'status': 'error', 'message': '日期格式错误'})
                dt = datetime.datetime.combine(dt_date, datetime.time.min)
                dt = timezone.make_aware(dt)
            else:
                # 解析包含时间的字符串
                dt = parse_datetime(time_str)
                if not dt:
                    return JsonResponse({'status': 'error', 'message': '时间格式错误'})
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)

            # 创建 CalendarEvent 时，将 dt 赋值给 start 字段
            models.CalendarEvent.objects.create(
                title=title,
                start=dt,
                user=request.tracer.user,  # 根据你的模型调整
                allDay=allDay,
                type='2'
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})
