from asyncio import current_task
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.db import transaction
from .models import Task, TaskChange
from .serializers import TaskSerializer, TaskChangeSerializer
from .filters import TaskFilter, TaskChangeFilter


class TaskViewSet(ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user, deleted=False)

    def save_task(self, serializer, update=False):
        _priority = serializer.validated_data["priority"]
        try:
            current_task_id = serializer.instance.id
        except AttributeError:
            current_task_id = None

        tasks = (
            Task.objects.filter(
                owner=self.request.user,
                priority__gte=_priority,
                deleted=False,
                completed=False,
            )
            .exclude(id=current_task_id)
            .select_for_update()
            .order_by("priority")
        )
        with transaction.atomic():
            bulk = []
            for task in tasks:
                if task.priority > _priority:
                    break
                _priority = task.priority = task.priority + 1
                bulk.append(task)
            if bulk:
                Task.objects.bulk_update(bulk, ["priority"], batch_size=1000)

            if update and serializer.validated_data.get("status"):
                TaskChange.objects.create(
                    task=serializer.instance,
                    previous_status=serializer.instance.status,
                    new_status=serializer.validated_data["status"],
                )
            serializer.save(owner=self.request.user)

    def perform_create(self, serializer):
        self.save_task(serializer)

    def perform_update(self, serializer):
        self.save_task(serializer, update=True)


class TaskChangeViewSet(ReadOnlyModelViewSet):

    queryset = TaskChange.objects.all()
    serializer_class = TaskChangeSerializer
    filterset_class = TaskChangeFilter

    def get_queryset(self):
        return TaskChange.objects.filter(task__owner=self.request.user)
