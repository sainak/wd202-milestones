from django.contrib.auth.models import User
from django.db import models


STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(models.Model):

    _previous_priority = None
    _previous_status = None

    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    priority = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_priority = self.priority
        self._previous_status = self.status
        # Attached signals:
        #   .signals.handlers.save_task

    def __str__(self):
        return self.title


class TaskChange(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.previous_status} -> {self.new_status}"

    @classmethod
    def add_change(cls, task: Task):
        if task._previous_status != task.status:
            cls.objects.create(
                task=task,
                previous_status=task._previous_status,
                new_status=task.status,
            )
