from django.forms import Form
from django.http import HttpResponseRedirect
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
from django.db import transaction

class BaseTaskView(ObjectOwnerMixin):
    model = Task
    queryset = Task.objects.filter(deleted=False).order_by("-priority")
    form_class = TaskForm
    context_object_name = "tasks"
    success_url = "/tasks/"

    def form_valid(self, form):
        # if its delete, we don't need to set the user or perform increments
        if self.request.POST.get("confirm_delete") is not None:
            return super().form_valid(form)

        form.instance.user = self.request.user
        _priority = form.instance.priority
        tasks = Task.objects.filter(
            priority__gte=_priority, deleted=False, completed=False
        ).exclude(pk=form.instance.id).order_by("priority")
        bulk = []
        for task in tasks:
            if task.priority > _priority:
                break
            _priority = task.priority = task.priority + 1
            bulk.append(task)
        with transaction.atomic():
            if bulk:
                Task.objects.bulk_update(bulk, ["priority"], batch_size=100)
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TaskListView(BaseTaskView, ListView):
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["completed_tasks"] = self.queryset.filter(completed=True).count()
        context_data["total_tasks"] = self.queryset.count()
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        if status == "completed":
            queryset = queryset.filter(completed=True)
        elif status == "pending":
            queryset = queryset.filter(completed=False)
        return queryset


class TaskDetailView(BaseTaskView, DetailView):
    ...


class TaskCreateView(BaseTaskView, CreateView):
    ...


class TaskUpdateView(BaseTaskView, UpdateView):
    ...


class TaskDeleteView(BaseTaskView, DeleteView):
    form_class = Form
