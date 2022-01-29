from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

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


class TaskChangeViewSet(ReadOnlyModelViewSet):

    queryset = TaskChange.objects.all()
    serializer_class = TaskChangeSerializer
    filterset_class = TaskChangeFilter

    def get_queryset(self):
        return TaskChange.objects.filter(task__owner=self.request.user)
