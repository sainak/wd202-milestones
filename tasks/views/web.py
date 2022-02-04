from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_filters.views import FilterView

from tasks.filters import TaskFilter
from tasks.forms import TaskForm, UserSettingsForm
from tasks.mixins import ObjectOwnerMixin
from tasks.models import Task, TaskChange, UserSettings


class BaseTaskView(ObjectOwnerMixin, LoginRequiredMixin):
    model = Task
    queryset = Task.objects.filter(deleted=False).order_by("-priority")
    form_class = TaskForm
    context_object_name = "tasks"
    success_url = reverse_lazy("tasks-list")


class TaskListView(BaseTaskView, FilterView):
    paginate_by = 5
    filterset_class = TaskFilter
    template_name = "tasks/task_list.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context_data["filtered_tasks"] = filter.qs.count()
        context_data["filtered_status"] = filter.data.get("status", "all").lower()
        context_data["total_tasks"] = self.queryset.count()
        return context_data


class TaskDetailView(BaseTaskView, DetailView):
    context_object_name = "task"


class TaskCreateView(BaseTaskView, CreateView):
    ...


class TaskUpdateView(BaseTaskView, UpdateView):
    ...


class TaskDeleteView(BaseTaskView, DeleteView):
    form_class = Form

    def form_valid(self, form):
        return super(DeleteView, self).form_valid(form)


class TaskHistoryView(LoginRequiredMixin, ListView):
    paginate_by = 8
    template_name = "tasks/task_history.html"
    context_object_name = "task_changes"
    queryset = TaskChange.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                task=self.kwargs["pk"],
                task__owner=self.request.user,
            )
            .order_by("-changed_at")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["task"] = Task.objects.get(pk=self.kwargs["pk"])
        return data


class UserSettingsView(LoginRequiredMixin, UpdateView):
    model = UserSettings
    form_class = UserSettingsForm
    template_name = "tasks/user_settings.html"
    success_url = reverse_lazy("tasks-list")

    def get_object(self):
        return UserSettings.objects.get_or_create(user=self.request.user)[0]
