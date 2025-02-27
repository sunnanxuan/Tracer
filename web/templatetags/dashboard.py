from django.template import Library
from web import models
from django.urls import reverse

from web.views.account import register

register = Library()


@register.simple_tag
def user_space(size):
    if size>=1024*1024*1024:
        return "%.2f GB"%(size/(1024*1024*1024),)
    elif size>=1024*1024:
        return "%.2f MB"%(size/(1024*1024),)
    elif size>=1024:
        return "%.2f KB"%(size/1024,)
    else:
        return "%.2f B"%size

