from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Task


class TaskForm(forms.ModelForm):

    error_css_class = "is-invalid"
    required_css_class = "is-required"

    class Meta:
        model = Task
        fields = ("title", "description", "priority", "completed")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def increment_priority(self, task):
        clash = (
            Task.objects.filter(priority=task.priority + 1).exclude(pk=task.pk).first()
        )
        if clash:
            self.increment_priority(clash)
        task.priority += 1
        task.save()

    def save(self, commit=True):
        clash = Task.objects.filter(
            user=self.instance.user, priority=self.instance.priority
        ).first()
        if clash:
            self.increment_priority(clash)
        return super().save(commit)
