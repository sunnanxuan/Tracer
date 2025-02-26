from django import template
from web.models import Notification  # 根据实际情况调整导入路径

register = template.Library()

@register.inclusion_tag('inclusion/notifications_list.html', takes_context=True)
def user_notifications(context):
    """
    获取当前用户的所有提示消息，按创建时间降序排列
    """
    request = context['request']
    notifications = Notification.objects.filter(user=request.tracer.user,is_read=0).order_by('-created_at')
    return {'notifications': notifications}



@register.simple_tag(takes_context=True)
def unread_notifications_count(context):
    """
    返回当前用户未读提示消息的数量
    """
    request = context['request']
    return Notification.objects.filter(user=request.tracer.user, is_read=False).count()
