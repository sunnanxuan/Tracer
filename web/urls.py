from django.contrib import admin
from django.urls import path,include
from web.views import account, index, project, manage, wiki



urlpatterns = [
    path("register/", account.register, name='register'),
    path("send/sms/", account.send_sms, name='send_sms'),
    path("login/sms/", account.login_sms, name='login_sms'),
    path("login/", account.login, name='login'),
    path("logout/", account.logout, name='logout'),
    path("image/code/", account.image_code, name='image_code'),

    path("index/", index.index, name='index'),

    path("project/list/", project.project_list, name='project_list'),
    path("project/star/<str:project_type>/<int:project_id>/", project.project_star, name='project_star'),
    path("project/unstar/<str:project_type>/<int:project_id>/", project.project_unstar, name='project_unstar'),
    path("manage/<int:project_id>/", include([
        path("dashboard/", manage.dashboard, name='dashboard'),
        path("issues/", manage.issues, name='issues'),
        path("statistics/", manage.statistics, name='statistics'),
        path("file/", manage.file, name='file'),
        path("wiki/", wiki.wiki, name='wiki'),
        path("setting/", manage.setting, name='setting'),

    ])),

]
