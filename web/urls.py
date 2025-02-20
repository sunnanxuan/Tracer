from django.contrib import admin
from django.urls import path,include
from web.views import account, index, project, statistics, wiki, file, setting, issues, dashboard,statistics



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
        path("dashboard/", dashboard.dashboard, name='dashboard'),
        path("dashboard/issues/chart/", dashboard.issues_chart, name='issues_chart'),

        path("statistics/", statistics.statistics, name='statistics'),
        path("statistics/priority/", statistics.statistics_priority, name='statistics_priority'),
        path("statistics/project/user/", statistics.statistics_project_user, name='statistics_project_user'),


        path("wiki/", wiki.wiki, name='wiki'),
        path("wiki/add", wiki.wiki_add, name='wiki_add'),
        path("wiki/catalog", wiki.wiki_catalog, name='wiki_catalog'),
        path("wiki/delete/<int:wiki_id>", wiki.wiki_delete, name='wiki_delete'),
        path("wiki/edit/<int:wiki_id>", wiki.wiki_edit, name='wiki_edit'),
        path("wiki/upload", wiki.wiki_upload, name='wiki_upload'),

        path("file/", file.file, name='file'),
        path("file/delete", file.file_delete, name='file_delete'),
        path('file/upload/', file.upload_file, name='upload_file'),
        path('file/download/', file.download_file, name='download_file'),

        path("setting/", setting.setting, name='setting'),
        path("setting/delete", setting.setting_delete, name='setting_delete'),

        path("issues/", issues.issues, name='issues'),
        path("issues/detail/<int:issues_id>", issues.issues_detail, name='issues_detail'),
        path("issues/record/<int:issues_id>", issues.issues_record, name='issues_record'),
        path("issues/change/<int:issues_id>", issues.issues_change, name='issues_change'),
        path("issues/invite/url", issues.invite_url, name='invite_url'),

    ])),
    path("invite/join/<str:code>", issues.invite_join, name='invite_join'),

]
