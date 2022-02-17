import datetime

from django.core.exceptions import ValidationError
from django.forms.fields import TimeField
from django.utils.timezone import localtime


class TzAwareTimeField(TimeField):
    def prepare_value(self, value):
        if isinstance(value, datetime.datetime):
            value = localtime(value)
        return super().prepare_value(value)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.time):
            return localtime().replace(
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                microsecond=value.microsecond,
            )
        if isinstance(value, datetime.datetime):
            return value
        value = value.strip()
        for format in self.input_formats:
            try:
                return self.strptime(value, format)
            except (ValueError, TypeError):
                continue
        raise ValidationError(self.error_messages["invalid"], code="invalid")

    def clean(self, value):
        value = self.to_python(value)
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.time):
            return localtime().replace(
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                microsecond=value.microsecond,
            )
        if isinstance(value, datetime.datetime):
            return value
