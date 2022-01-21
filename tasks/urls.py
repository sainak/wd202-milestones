from django.urls import path

from tasks.views import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

urlpatterns = [
    path("", TaskListView.as_view(), name="tasks-list"),
    path("create/", TaskCreateView.as_view(), name="tasks-create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="tasks-detail"),
    path("update/<int:pk>/", TaskUpdateView.as_view(), name="tasks-update"),
    path("delete/<int:pk>/", TaskDeleteView.as_view(), name="tasks-delete"),
]
