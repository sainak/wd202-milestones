from django.contrib import admin

from .models import Task, TaskChange, UserSettings


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "priority", "status", "deleted")
    list_display_links = ("id", "title")
    list_filter = ("created_at", "status")
    search_fields = ("title", "description")
    readonly_fields = ("created_at",)


admin.site.register(TaskChange)
admin.site.register(UserSettings)
