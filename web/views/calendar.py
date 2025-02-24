
import json
from django.http import JsonResponse
from django.shortcuts import render
from web import models
from django.views.decorators.http import require_POST




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
                'color': '#008B8B'
            })
    return JsonResponse(events, safe=False)





@require_POST
def add_calendar_event(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        start = data.get('start')
        # 保存手动添加的事件
        print(start)
        event = models.CalendarEvent.objects.create(
            user=request.tracer.user,
            title=title,
            start=start,
            type=2,
        )
        return JsonResponse({'status': 'success', 'id': event.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
