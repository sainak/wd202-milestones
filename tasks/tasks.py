from inspect import cleandoc as _

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count

from tasks.models import Task


def generate_report(user):
    status = (
        Task.objects.filter(
            owner=user,
            deleted=False,
        )
        .order_by("status")
        .values("status")
        .annotate(count=Count("status"))
    )

    report = _(
        f"""
        Hi {user.username},

        Here is your daily tasks report:
        """
    )

    if not status:
        report += _("\nNo tasks to report.")
    for s in status:
        report += _(f"\n{s['status'].title().replace('_', ' ')}: {s['count']}")

    return report


@shared_task
def send_report(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        print(e)
        return

    send_mail(
        "Daily Task Report",
        generate_report(user),
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
