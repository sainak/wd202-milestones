from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils.timezone import datetime, now
from django_celery_beat.models import IntervalSchedule, PeriodicTask

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_priority = self.priority
        self._previous_status = self.status

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if self.status == "COMPLETED":
            super().save(*args, **kwargs)
            return

        clashing_priority = self.priority

        clashing_tasks = (
            Task.objects.filter(
                owner=self.owner,
                priority__gte=clashing_priority,
                deleted=False,
            )
            .exclude(
                id=self.id,
                status="COMPLETED",
            )
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
                if db_backend == "sqlite3":
                    # https://www.sqlite.org/limits.html#max_sql_length
                    bulk_update_kwargs["batch_size"] = 500

                Task.objects.bulk_update(bulk, ["priority"], **bulk_update_kwargs)

            super().save(*args, **kwargs)


class TaskChange(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.owner.username}: {self.task.title} - {self.previous_status} -> {self.new_status}"


class UserSettings(models.Model):
    _previous_report_time = None

    send_report = models.BooleanField(default=False)
    report_time = models.TimeField(default="00:00:00")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    send_report_task = models.OneToOneField(
        PeriodicTask, on_delete=models.CASCADE, null=True, blank=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_report_time = self.report_time

    def __str__(self):
        return f"{self.user.username}'s settings"

    def save(self, *args, **kwargs):
        if not self.send_report and self.send_report_task:
            try:
                self.send_report_task.delete()
            except (PeriodicTask.DoesNotExist, AttributeError):
                pass

        if self.send_report and self.report_time != self._previous_report_time:
            try:
                self.send_report_task.delete()
            except (PeriodicTask.DoesNotExist, AttributeError):
                pass

            self.send_report_task = PeriodicTask.objects.create(
                name=f"Send report to {self.user.username}",
                task="tasks.tasks.send_report",
                interval=IntervalSchedule.objects.get_or_create(
                    every=1, period=IntervalSchedule.DAYS
                )[0],
                start_time=datetime.combine(now(), self.report_time),
                args=[self.user.id],
                enabled=True,
            )
        super().save(*args, **kwargs)
