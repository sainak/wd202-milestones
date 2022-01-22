from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date", "completed", "deleted")
    list_display_links = ("id", "title")
    list_filter = ("created_date",)
    search_fields = ("title", "description")
    readonly_fields = ("created_date",)
