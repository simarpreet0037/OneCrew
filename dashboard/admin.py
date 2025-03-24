from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import User, ProjectMaster, JobMaster, Employee, WorkOrder, NewHire

admin.site.register(User)
admin.site.register(ProjectMaster)
admin.site.register(JobMaster)
admin.site.register(Employee)
admin.site.register(WorkOrder)
admin.site.register(NewHire)
