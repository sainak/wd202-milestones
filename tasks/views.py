from django.db import transaction
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from .filters import TaskChangeFilter, TaskFilter
from .models import Task, TaskChange
from .serializers import TaskChangeSerializer, TaskSerializer


class TaskViewSet(ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class TaskChangeViewSet(mixins.ListModelMixin, GenericViewSet):

    queryset = TaskChange.objects.all()
    serializer_class = TaskChangeSerializer
    filterset_class = TaskChangeFilter

    def get_queryset(self):
        return TaskChange.objects.filter(
            task=self.kwargs["task_pk"],
            task__owner=self.request.user,
        )
