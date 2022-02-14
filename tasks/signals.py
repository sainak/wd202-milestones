from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task, TaskChange


@receiver(post_save, sender=Task, dispatch_uid="task.signals.0001_task_post_save")
def task_status_changed(sender, instance, created, raw, **kwargs):
    if created or raw:
        return

    if instance._initial_status != instance.status:
        TaskChange.objects.create(
            task=instance,
            previous_status=instance._initial_status,
            new_status=instance.status,
        )
