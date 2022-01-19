from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from .models import Task


tasks = []
completed_tasks = []


def all_tasks_view(request):
    search_task = request.GET.get("search")
    all_tasks = Task.objects.all().filter(deleted=False)
    if search_task:
        all_tasks = all_tasks.filter(title__icontains=search_task)
    tasks = all_tasks.filter(completed=False)
    completed_tasks = all_tasks.filter(completed=True)
    return render(
        request,
        "all_tasks.html",
        {
            "tasks": tasks,
            "completed_tasks": completed_tasks,
        },
    )


def task_view(request):
    search_task = request.GET.get("search")
    tasks = Task.objects.all().filter(deleted=False, completed=False)
    if search_task:
        tasks = tasks.filter(title__icontains=search_task)
    return render(request, "tasks.html", {"tasks": tasks})


def completed_tasks_view(request):
    completed_tasks = Task.objects.filter(completed=True, deleted=False)
    return render(request, "completed_tasks.html", {"completed_tasks": completed_tasks})


def add_task_view(request):
    task_value = request.GET.get("task")
    task = Task(title=task_value)
    if request.user.is_authenticated:
        task.user = request.user
    task.save()
    return HttpResponseRedirect("/all_tasks")


def delete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.deleted = True
    task.save()
    return HttpResponseRedirect("/all_tasks")


def complete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed = True
    task.save()
    return HttpResponseRedirect("/all_tasks")
