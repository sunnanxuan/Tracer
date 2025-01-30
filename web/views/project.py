from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from web.forms.project import ProjectModelForm
from web import models



def project_list(request):
    if request.method == 'GET':
        project_dict ={'star':[], 'my':[], 'join':[]}
        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append(row)
            else:
                project_dict['my'].append(row)
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['join'].append(item.project)
            else:
                project_dict['my'].append(item.project)
        form = ProjectModelForm(request)
        return render(request,'project_list.html',{'form':form, 'project_dict':project_dict})

    form = ProjectModelForm(request,data=request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status':True})

    return JsonResponse({'status':False, 'errors':form.errors})





def project_star(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(id=project_id, user=request.tracer.user).update(star=False)
        return redirect('project_list')
    return HttpResponse('请求错误')
