from datetime import time

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils.timezone import localtime, timedelta

from task_manager.mixins import PreserveInitialFieldValueMixin

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(PreserveInitialFieldValueMixin, models.Model):

    _preserved_fields = ("priority", "status")

    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if self.status == "COMPLETED" or (
            self.pk and self._initial_priority == self.priority
        ):
            super().save(*args, **kwargs)
            return

        clashing_priority = self.priority

        clashing_tasks = (
            Task.objects.filter(
                owner=self.owner,
                priority__gte=clashing_priority,
                deleted=False,
                status__in=("PENDING", "IN_PROGRESS"),
            )
            .exclude(id=self.id)
            .select_for_update()
            .order_by("priority")
        )

        with transaction.atomic():
            bulk = []
            for task in clashing_tasks:
                if task.priority > clashing_priority:
                    break
                clashing_priority = task.priority = task.priority + 1
                bulk.append(task)

            if bulk:
                bulk_update_kwargs = {}

                db_backend = settings.DATABASES[self._state.db]["ENGINE"].split(".")[-1]
                if db_backend == "sqlite3":  # pragma: no cover
                    # https://www.sqlite.org/limits.html#max_sql_length
                    bulk_update_kwargs["batch_size"] = 500

                Task.objects.bulk_update(bulk, ["priority"], **bulk_update_kwargs)

            super().save(*args, **kwargs)


class TaskChange(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="changes")
    previous_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.owner.username}: {self.task.title} - {self.previous_status} -> {self.new_status}"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    send_report = models.BooleanField(default=False)
    report_time = models.TimeField(default=time(0, 0, 0))
    last_report_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s settings"

    def save(self, *args, **kwargs):
        if self.send_report:
            current_time = localtime()
            report_time = current_time.replace(
                hour=self.report_time.hour, minute=self.report_time.minute, second=0
            )
            if (
                not self.last_report_sent_at
                # avoid sending multiple reports on the same day
                or self.last_report_sent_at <= current_time - timedelta(days=1)
            ):
                self.last_report_sent_at = report_time - timedelta(days=1)
            else:
                self.last_report_sent_at = report_time
        super().save(*args, **kwargs)
