from django.template import Library
from web import models
from django.urls import reverse

from web.views.account import register

register = Library()


@register.simple_tag
def string_just(num):
    if num<100:
        num=str(num).rjust(3,'0')
    return '#{}'.format(num)
