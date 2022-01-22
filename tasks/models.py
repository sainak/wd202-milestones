from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    priority = models.IntegerField()
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "priority",
                "user",
                condition=(Q(deleted=False) & Q(completed=False)),
                name="unique_task_priority",
            )
        ]
