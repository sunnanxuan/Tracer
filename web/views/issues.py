from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.issues import IssueModelForm
from web import models
from django.shortcuts import get_object_or_404




def issues(request, project_id):
    if request.method == 'GET':
        project = get_object_or_404(models.Project, id=project_id)
        issues_queryset = models.Issues.objects.filter(project=project).order_by('-create_datetime')
        form = IssueModelForm(request)
        context = {
            'issues_list': issues_queryset,
            'form': form,
        }
        return render(request, 'issues.html', context)


    print('到这里')

    form = IssueModelForm(request,data=request.POST)
    if form.is_valid():
        form.instance.project=request.tracer.project
        form.instance.creator=request.tracer.user
        form.save()
        return JsonResponse({'status':True})

    return JsonResponse({'status':False, 'error':form.errors})

