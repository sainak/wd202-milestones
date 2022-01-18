from django.contrib import admin
from django.urls import path

from tasks import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", views.task_view),
    path("add-task/", views.add_task_view),
    path("delete-task/<int:index>/", views.delete_task_view),
]
