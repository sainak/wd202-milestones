from datetime import datetime, timedelta

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.schedules import crontab
from celery.utils.log import get_logger
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count

from task_manager.celery import app
from tasks.models import Task, UserSettings

logger = get_logger(__name__)


def send_report(user):
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
    report = f"Hi {user.username},\n\n"
    if not status:
        report += "\nNo tasks to report today."
    else:
        report += "\nHere is your daily tasks report:\n"
        for s in status:
            _sn = s["status"].title().replace("_", " ")
            _sc = s["count"]
            report += f"\n{_sn} task{'s'[:_sc^1]}: {_sc}"

    send_mail("Daily Task Report", report, settings.EMAIL_HOST_USER, [user.email])


@shared_task(
    bind=True,
    default_retry_delay=30,
    max_retries=3,
)
def send_report_celery_task(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        logger.error(f"send_report: User with id {user_id} does not exist")
        return
    try:
        logger.info(f"send_report: Sending report to {user.username}")
        send_report(user)
    except Exception as e:
        try:
            logger.error(
                f"send_report: Failed to send report for user {user_id} retrying..."
            )
            raise send_report_celery_task.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(f"send_report: Max retries exceeded for user {user_id}")
            # user.settings.last_report_sent_at = (
            #     user.settings.last_report_sent_at - timedelta(days=1)
            # )
            # user.settings.save()
            raise


@shared_task
def fetch_user_settings():
    logger.info("fetch_user_settings: Started")
    now = datetime.now()
    users_configs_to_report = UserSettings.objects.filter(
        send_report=True,
        report_time__range=(
            now.time() - timedelta(seconds=30),
            now.time() + timedelta(seconds=30),
        ),
        last_report_sent_at__lt=now.date(),
    ).select_related("user")

    logger.info(f"fetch_user_settings: {len(users_configs_to_report)} users to report")
    for user_config in users_configs_to_report:
        send_report_celery_task.delay(user_config.user.id)
        user_config.last_report_sent_at = datetime.now()
        user_config.save()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.conf.beat_schedule["fetch_user_settings"] = {
        "task": "tasks.fetch_user_settings",
        "schedule": crontab(minute="*"),
    }
