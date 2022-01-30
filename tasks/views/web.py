from django.forms import Form
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django_filters.views import FilterView

from tasks.filters import TaskFilter
from tasks.forms import TaskForm
from tasks.mixins import ObjectOwnerMixin
from tasks.models import Task


class BaseTaskView(ObjectOwnerMixin):
    model = Task
    queryset = Task.objects.filter(deleted=False).order_by("-priority")
    form_class = TaskForm
    context_object_name = "tasks"
    success_url = "/tasks/"

    def form_valid(self, form):
        # if self.request.POST.get("confirm_delete") is not None:
        #     # if its delete, we don't need to set the user or perform increments
        #     return super().form_valid(form)

        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskListView(BaseTaskView, FilterView):
    paginate_by = 5
    filterset_class = TaskFilter
    template_name = "tasks/task_list.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context_data["completed_tasks"] = self.queryset.filter(
            status="completed"
        ).count()
        context_data["total_tasks"] = self.queryset.count()
        return context_data

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     status = self.request.GET.get("status")
    #     if status == "completed":
    #         queryset = queryset.filter(completed=True)
    #     elif status == "pending":
    #         queryset = queryset.filter(completed=False)
    #     return queryset


class TaskDetailView(BaseTaskView, DetailView):
    ...


class TaskCreateView(BaseTaskView, CreateView):
    ...


class TaskUpdateView(BaseTaskView, UpdateView):
    ...


class TaskDeleteView(BaseTaskView, DeleteView):
    form_class = Form

    def form_valid(self, form):
        return super(DeleteView, self).form_valid(form)
