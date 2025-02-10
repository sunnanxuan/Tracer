from django.contrib import admin
from .models import UserInfo, PricePolicy, Transaction, Project, ProjectUser, Issues, IssuesType, Module

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(PricePolicy)
admin.site.register(Transaction)
admin.site.register(Project)
admin.site.register( ProjectUser)
admin.site.register(Issues)
admin.site.register(IssuesType)
admin.site.register( Module)

