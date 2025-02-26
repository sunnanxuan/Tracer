from django.shortcuts import render
from django.http import JsonResponse
from web.models import Notification
from django.shortcuts import render, get_object_or_404

def notifications_page(request):
    # 按未读在前、创建时间降序排序
    notifications = Notification.objects.filter(user=request.tracer.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

def notification_read(request, notification_id):
    notifications = Notification.objects.filter(user=request.tracer.user).order_by('-created_at')
    # 获取指定通知，确保当前用户拥有
    notification = get_object_or_404(Notification, id=notification_id, user=request.tracer.user)
    # 如果未读，则标记为已读
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return render(request, 'notification_read.html', {
        'notifications': notifications,
        'expanded_notification_id': notification.id,
    })
