import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if tz := request.session.get("django_timezone"):
            timezone.activate(zoneinfo.ZoneInfo(tz))
        else:
            try:
                tz = request.user.settings.timezone
                request.session["django_timezone"] = tz
                timezone.activate(zoneinfo.ZoneInfo(tz))
            except AttributeError:
                timezone.deactivate()
        return self.get_response(request)
