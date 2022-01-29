from django.db import transaction
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from tasks.filters import TaskChangeFilter, TaskFilter
from tasks.models import Task, TaskChange
from tasks.serializers import TaskChangeSerializer, TaskSerializer


class TaskViewSet(ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskChangeViewSet(mixins.ListModelMixin, GenericViewSet):

    queryset = TaskChange.objects.all()
    serializer_class = TaskChangeSerializer
    filterset_class = TaskChangeFilter

    def get_queryset(self):
        return TaskChange.objects.filter(
            task=self.kwargs["task_pk"],
            task__owner=self.request.user,
        )
