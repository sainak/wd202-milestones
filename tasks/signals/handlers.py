from django.conf import settings
from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from tasks.models import Task, TaskChange


@receiver(pre_save, sender=Task)
def save_task(sender, instance: Task, raw, using, **kwargs):

    if raw:
        # don't do anything when using raw queries
        return

    if instance.status == "COMPLETED":
        TaskChange.add_change(instance)
        return

    clashing_priority = instance.priority

    clashing_tasks = (
        Task.objects.filter(
            owner=instance.owner,
            priority__gte=clashing_priority,
            deleted=False,
        )
        .exclude(
            id=instance.id,
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

            db_backend = settings.DATABASES[using]["ENGINE"].split(".")[-1]
            if db_backend == "sqlite3":
                # https://www.sqlite.org/limits.html#max_sql_length
                bulk_update_kwargs["batch_size"] = 500

            Task.objects.bulk_update(bulk, ["priority"], **bulk_update_kwargs)

        TaskChange.add_change(instance)
