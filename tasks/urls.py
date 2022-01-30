from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework_nested import routers

from .views.api import TaskChangeViewSet, TaskViewSet
from .views.web import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    UserSettingsView,
)

web_urlpatterns = [
    path("", TaskListView.as_view(), name="tasks-list"),
    path("create/", TaskCreateView.as_view(), name="tasks-create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="tasks-detail"),
    path("update/<int:pk>/", TaskUpdateView.as_view(), name="tasks-update"),
    path("delete/<int:pk>/", TaskDeleteView.as_view(), name="tasks-delete"),
    path("settings/", UserSettingsView.as_view(), name="user-settings"),
]

router = routers.DefaultRouter(trailing_slash=False)
router.register("task", TaskViewSet)

task_history = routers.NestedDefaultRouter(router, "task", lookup="task")
task_history.register(r"history", TaskChangeViewSet, basename="task-history")

api_urlpatterns = [
    path("", include(router.urls)),
    path("", include(task_history.urls)),
]

urlpatterns = [
    path("api/", include(api_urlpatterns)),
    path("tasks/", include(web_urlpatterns)),
    path("", RedirectView.as_view(url="/tasks/")),
]
