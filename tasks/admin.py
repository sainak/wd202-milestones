from django.contrib import admin

from tasks.models import Task

# Register your models here.


admin.sites.site.register(Task)
