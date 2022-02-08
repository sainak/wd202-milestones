from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from celery import current_app, shared_task
from celery.schedules import crontab
from celery.utils.log import get_logger
from django.conf import settings
from django.db import transaction
from django.db.models import Count

from tasks.models import Task, UserSettings

logger = get_logger(__name__)


def send_report(user):
    # raise Exception("Sending report failed")
    status = (
        Task.objects.filter(
            owner=user,
            deleted=False,
        )
        .order_by("status")
        .values("status")
        .annotate(count=Count("status"))
    )

    # TODO: use template to make this beautiful and add unsubscribe link
    report = f"Hi {user.get_full_name() or user.username},\n\n"
    if not status:
        report += "\nNo tasks to report today."
    else:
        report += "\nHere is your daily tasks report:\n"
        for s in status:
            _sn = s["status"].title().replace("_", " ")
            _sc = s["count"]
            report += f"\n{_sn} task{'s'[:_sc^1]}: {_sc}"

    user.email_user(
        subject="Daily tasks report",
        message=report,
        from_email=settings.EMAIL_HOST_USER,
    )


@shared_task
def fetch_user_settings():
    logger.info("fetch_user_settings: Started")
    now = datetime.now().replace(tzinfo=ZoneInfo(settings.CELERY_TIMEZONE))

    users_configs_to_report = (
        UserSettings.objects.filter(
            send_report=True,
            last_report_sent_at__lt=now - timedelta(days=1),
        )
        .select_related("user")
        .select_for_update()
    )

    with transaction.atomic():
        logger.info(
            f"fetch_user_settings: {len(users_configs_to_report)} users to report"
        )
        for user_config in users_configs_to_report:
            logger.info(
                f"fetch_user_settings: Sending report to [{user_config.user.id}]:{user_config.user.username}"
            )
            send_report(user_config.user)
            user_config.last_report_sent_at = now.replace(
                hour=user_config.report_time.hour,
                minute=user_config.report_time.minute,
                second=0,
            )
            user_config.save()


@current_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.conf.beat_schedule["fetch_user_settings"] = {
        "task": "tasks.tasks.fetch_user_settings",
        "schedule": crontab(minute="*"),
    }
