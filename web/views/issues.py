from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.issues import IssueModelForm
from web import models
from django.shortcuts import get_object_or_404
from utils.pagination import Pagination




def issues(request, project_id):
    if request.method == 'GET':
        queryset = models.Issues.objects.filter(project_id=project_id).order_by('-create_datetime')
        page_object=Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=1
        )
        issues_list=queryset[page_object.start:page_object.end]
        form = IssueModelForm(request)
        context = {
            'issues_list': issues_list,
            'form': form,
            'page_html': page_object.page_html(),
        }
        return render(request, 'issues.html', context)

    form = IssueModelForm(request,data=request.POST)
    if form.is_valid():
        form.instance.project=request.tracer.project
        form.instance.creator=request.tracer.user
        form.save()
        return JsonResponse({'status':True})

    return JsonResponse({'status':False, 'error':form.errors})

