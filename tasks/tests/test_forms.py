from django.contrib.auth.models import User
from django.test import TestCase

from tasks.forms import TaskForm, UserSettingsForm
from tasks.models import Task, UserSettings


class TaskFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_valid_task_form(self):
        form = TaskForm(
            data={
                "title": "test title",
                "description": "test description",
                "priority": 1,
                "status": "PENDING",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_task_form(self):
        form = TaskForm(
            data={
                "title": "test title",
                "description": "test description",
                "priority": 1,
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_task_save(self):
        form = TaskForm(
            data={
                "title": "test title 6",
                "description": "test description",
                "priority": 1,
                "status": "PENDING",
            }
        )
        form.instance.owner = self.user
        form.save()
        self.assertTrue(
            Task.objects.filter(owner=self.user, title="test title 6").exists()
        )


class UserSettingsFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_valid_user_settings_form(self):
        form = UserSettingsForm(
            data={
                "send_report": True,
                "report_time": "00:00:00",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_user_settings_form(self):
        form = UserSettingsForm(
            data={
                "send_report": True,
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_user_settings_save(self):
        form = UserSettingsForm(
            data={
                "send_report": True,
                "report_time": "00:00:00",
            }
        )
        form.instance.user = self.user
        form.save()
        self.assertTrue(UserSettings.objects.filter(user=self.user).exists())
