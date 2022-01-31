from django import forms

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

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

    class Meta:
        model = UserSettings
        fields = ("report_time", "send_report")
        widgets = {
            "report_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "send_report": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
