import django_filters

from .models import STATUS_CHOICES, Task, TaskChange


class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = Task
        fields = (
            "title",
            "status",
        )


class TaskChangeFilter(django_filters.FilterSet):
    previous_status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)
    new_status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = TaskChange
        fields = (
            "previous_status",
            "new_status",
            "changed_at",
        )
