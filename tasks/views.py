from django.forms import Form
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import TaskForm
from .mixins import ObjectOwnerMixin
from .models import Task


class BaseTaskView(ObjectOwnerMixin):
    model = Task
    queryset = Task.objects.filter(deleted=False).order_by("-priority")
    form_class = TaskForm
    context_object_name = "tasks"
    success_url = "/tasks/"


class TaskListView(BaseTaskView, ListView):
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["completed_tasks"] = self.queryset.filter(completed=True).count()
        context_data["total_tasks"] = self.queryset.count()
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        if status == "completed":
            return queryset.filter(completed=True)
        elif status == "pending":
            return queryset.filter(completed=False)
        return queryset


class TaskDetailView(BaseTaskView, DetailView):
    ...


class TaskCreateView(BaseTaskView, CreateView):
    ...


class TaskUpdateView(BaseTaskView, UpdateView):
    ...


class TaskDeleteView(BaseTaskView, DeleteView):
    form_class = Form
