from django.shortcuts import render
from django.http import JsonResponse
from web.models import Notification
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render
from web.models import Notification
from utils.pagination import Pagination

def notifications_page(request):
    # 获取当前用户的所有通知，按创建时间降序排列
    notifications_all = Notification.objects.filter(user=request.tracer.user).order_by('-created_at')
    all_count = notifications_all.count()
    # 获取当前页数，默认为 1
    current_page = request.GET.get('page', 1)
    # 实例化分页插件，每页显示 10 条通知
    pagination = Pagination(current_page, all_count, request.path_info, request.GET, per_page=5)
    # 切片获取当前页数据
    notifications = notifications_all[pagination.start:pagination.end]
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'pagination_html': pagination.page_html()
    })


def notification_read(request, notification_id):
    # 获取当前用户所有通知，按创建时间降序排列（未读优先可以另外调整排序规则）
    notifications_all = Notification.objects.filter(user=request.tracer.user).order_by('-created_at')

    # 获取指定通知，确保当前用户拥有
    notification = get_object_or_404(Notification, id=notification_id, user=request.tracer.user)

    # 如果通知未读，则标记为已读
    if not notification.is_read:
        notification.is_read = True
        notification.save()

    # 假设每页显示10条通知
    per_page = 5
    total_count = notifications_all.count()

    # 计算指定通知在整个列表中的位置
    # 这里使用 created_at 大于当前通知的数量作为位置
    pos = notifications_all.filter(created_at__gt=notification.created_at).count()
    # 当前页号：pos 从0开始计数，页号从1开始
    current_page = pos // per_page + 1

    # 创建分页对象
    pagination = Pagination(current_page, total_count, request.path_info, request.GET, per_page=per_page)
    # 切片获取当前页通知
    notifications = notifications_all[pagination.start:pagination.end]

    return render(request, 'notification_read.html', {
        'notifications': notifications,
        'pagination_html': pagination.page_html(),
        'expanded_notification_id': notification.id,
    })
