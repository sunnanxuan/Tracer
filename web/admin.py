from django.contrib import admin
from .models import UserInfo, PricePolicy, Transaction, Project, ProjectUser

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(PricePolicy)
admin.site.register(Transaction)
admin.site.register(Project)
admin.site.register( ProjectUser)

