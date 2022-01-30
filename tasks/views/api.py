from django.db import transaction
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from tasks.filters import TaskChangeFilter, TaskFilter
from tasks.mixins import ObjectOwnerMixin
from tasks.models import Task, TaskChange
from tasks.serializers import TaskChangeSerializer, TaskSerializer


class TaskViewSet(ObjectOwnerMixin, ModelViewSet):
    queryset = Task.objects.filter(deleted=False)
    serializer_class = TaskSerializer
    filterset_class = TaskFilter


class TaskChangeViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = TaskChange.objects.all()
    serializer_class = TaskChangeSerializer
    filterset_class = TaskChangeFilter

    def get_queryset(self):
        return TaskChange.objects.filter(
            task=self.kwargs["task_pk"],
            task__owner=self.request.user,
        )
