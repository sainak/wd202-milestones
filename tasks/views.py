from django.shortcuts import render
from django.http import HttpResponseRedirect

tasks = []
completed_tasks = []


def task_view(request):
    return render(request, "tasks.html", {"tasks": tasks})


def completed_tasks_view(request):
    return render(request, "completed_tasks.html", {"completed_tasks": completed_tasks})


def add_task_view(request):
    task_value = request.GET.get("task")
    if task_value:
        tasks.append(task_value)
    return HttpResponseRedirect("/tasks")


def delete_task_view(request, index):
    if index:
        del tasks[index - 1]
    return HttpResponseRedirect("/tasks")


def complete_task_view(request, index):
    if index:
        completed_tasks.append(tasks.pop(index - 1))
    return HttpResponseRedirect("/tasks")