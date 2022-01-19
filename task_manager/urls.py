from django.contrib import admin
from django.urls import path

from tasks import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("all_tasks/", views.all_tasks_view),
    path("tasks/", views.task_view),
    path("completed_tasks/", views.completed_tasks_view),
    path("add-task/", views.add_task_view),
    path("delete-task/<int:pk>/", views.delete_task_view),
    path("complete_task/<int:pk>/", views.complete_task_view),
]
