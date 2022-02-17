from django import forms
from django.utils.timezone import localtime

from task_manager.fields import TzAwareTimeField

from .models import Task, UserSettings


class TaskForm(forms.ModelForm):

    error_css_class = "is-invalid"
    required_css_class = "is-required"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Task
        fields = ("title", "description", "priority", "status")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class UserSettingsForm(forms.ModelForm):

    error_css_class = "is-invalid"
    required_css_class = "is-required"

    report_time = TzAwareTimeField(
        label="Report time",
        widget=forms.TimeInput(
            attrs={"class": "form-control", "type": "time"}, format="%H:%M"
        ),
        initial=localtime().replace(hour=0, minute=0, second=0, microsecond=0),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

    class Meta:
        model = UserSettings
        fields = ("send_report", "report_time", "timezone")
        widgets = {
            "send_report": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "timezone": forms.Select(attrs={"class": "form-control"}),
        }
