import django_filters
from django.forms import widgets

from django.utils.timezone import now

from .models import Task, TaskChange, STATUS_CHOICES

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
            "task",
            "previous_status",
            "new_status",
            "changed_at"
        )