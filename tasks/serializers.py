from rest_framework.serializers import ModelSerializer

from .models import Task, TaskChange


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_at",
            "completed",
            "owner",
        )
        read_only_fields = ("owner", "created_at")

    def save(self, **kwargs):
        return super().save(**kwargs)


class TaskChangeSerializer(ModelSerializer):
    class Meta:
        model = TaskChange
        fields = (
            "id",
            "task",
            "previous_status",
            "new_status",
            "changed_at",
        )
