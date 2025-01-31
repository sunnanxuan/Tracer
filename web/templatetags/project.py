from django.template import Library
from web import models

from web.views.account import register

register=Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_projects_list(request):
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)
    join_project_list=models.ProjectUser.objects.filter(user=request.tracer.user)
    return {'my':my_project_list,'join':join_project_list}