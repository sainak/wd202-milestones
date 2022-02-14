from datetime import time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import localtime

from tasks.models import Task, UserSettings
from tasks.tasks import fetch_user_settings, send_report


class CeleryTasksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        self.user_settings = UserSettings.objects.create(
            user=self.user,
            send_report=True,
            report_time=time(8, 0, 0),
            last_report_sent_at=localtime() - timedelta(days=2),
        )

    def test_send_report(self):
        Task.objects.bulk_create(
            [
                Task(title="test title 1", owner=self.user),
                Task(title="test title 2", owner=self.user),
                Task(title="test title 3", owner=self.user, status="IN_PROGRESS"),
                Task(title="test title 4", owner=self.user, status="COMPLETED"),
            ]
        )
        result, report = send_report(self.user)
        self.assertTrue(result)
        self.assertIn("Completed task: 1", report)
        self.assertIn("In Progress task: 1", report)
        self.assertIn("Pending tasks: 2", report)

    def test_send_report_no_tasks(self):
        result, report = send_report(self.user)
        self.assertTrue(result)
        self.assertIn("No tasks to report", report)

    def test_fetch_user_settings(self):
        fetch_user_settings()
        user_settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(
            user_settings.last_report_sent_at.date(),
            localtime().date(),
        )
