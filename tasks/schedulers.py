from datetime import datetime, timedelta

from celery.beat import Scheduler
from celery.schedules import crontab
from celery.utils.log import get_logger

from tasks.models import UserSettings


class DynamicScheduler(Scheduler):

    _schedule = {}
    logger = get_logger("DynamicScheduler")

    def __init__(self, *args, **kwargs):
        self._last_updated = datetime.now()
        self._schedule = self.get_entries_from_db()
        Scheduler.__init__(self, *args, **kwargs)

    def setup_schedule(self):
        super().setup_schedule()
        self.update_from_dict(self._schedule)
        self.print_schedule()

    def print_schedule(self):
        self.logger.info("**** Current Schedule ****")
        for name, schedule in self.data.items():
            self.logger.info(f"{name}: {schedule}")

    def requires_update(self):
        return (
            self._last_updated + timedelta(seconds=self.max_interval) < datetime.now()
        )

    def get_entries_from_db(self):
        try:
            users_configs_to_report = (
                UserSettings.objects.filter(
                    send_report=True,
                )
                .select_related("user")
                .values("user__id", "report_time", "send_report_task_id")
            )

            entries = {}
            for user_config in users_configs_to_report:
                entries[user_config["send_report_task_id"]] = {
                    "task": "send_report",
                    # "schedule": schedule(
                    #     run_every=10.0,
                    # ),
                    "schedule": crontab(
                        hour=user_config["report_time"].hour,
                        minute=user_config["report_time"].minute,
                    ),
                    "args": (user_config["user__id"],),
                }

            return entries
        except Exception as e:
            self.logger.error(
                "Received exception while fetching schedule: {0}".format(e)
            )
            return self._schedule

    def get_schedule(self):
        if self.requires_update():
            self._last_updated = datetime.now()
            self._schedule = self.get_entries_from_db()
            self.data = {}
            self.setup_schedule()
        return self.data

    def set_schedule(self, schedule):
        self.data = schedule

    schedule = property(get_schedule, set_schedule)
