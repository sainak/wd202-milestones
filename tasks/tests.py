from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from .models import TaskChange, UserSettings, Task
from .forms import TaskForm, UserSettingsForm


class TasksModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_create_task(self):
        task = Task.objects.create(
            title="test title 1",
            description="test description",
            priority=1,
            owner=self.user,
        )
        self.assertTrue(
            Task.objects.filter(owner=self.user, title="test title 1").exists()
        )
        self.assertEqual(str(task), "test title 1")

    def test_task_history(self):
        task = Task.objects.create(
            title="test title",
            description="test description",
            priority=1,
            owner=self.user,
        )
        task.status = "COMPLETED"
        task.save()
        task_change = TaskChange.objects.filter(task=task).first()
        self.assertTrue(task_change)
        self.assertEqual(
            str(task_change), "testuser: test title - PENDING -> COMPLETED"
        )

    def test_task_history_with_no_changes(self):
        task = Task.objects.create(
            title="test title",
            description="test description",
            priority=1,
            owner=self.user,
        )
        task.status = "PENDING"
        task.save(force_update=True)
        task_change = TaskChange.objects.filter(task=task)
        self.assertEqual(task_change.count(), 0)

    def test_task_priority_increment(self):
        Task.objects.create(
            title="test title 1",
            description="test description",
            priority=3,
            owner=self.user,
        )
        task1 = Task.objects.create(
            title="test title 2",
            description="test description",
            priority=1,
            owner=self.user,
        )
        Task.objects.create(
            title="test title 3",
            description="test description",
            priority=1,
            owner=self.user,
        )
        task1 = Task.objects.get(pk=task1.pk)
        self.assertEqual(task1.priority, 2)

    def test_task_priority_does_not_increment(self):
        task1 = Task.objects.create(
            title="test title",
            description="test description",
            priority=1,
            owner=self.user,
        )
        Task.objects.create(
            title="test title",
            description="test description",
            priority=1,
            status="COMPLETED",
            owner=self.user,
        )
        task1 = Task.objects.get(pk=task1.pk)
        self.assertEqual(task1.priority, 1)

    def test_create_user_settings(self):
        user_settings = UserSettings.objects.create(
            user=self.user,
            send_report=True,
            report_time="00:00:00",
        )
        self.assertEqual(str(user_settings), "testuser's settings")
        self.assertTrue(UserSettings.objects.filter(user=self.user).exists())


class TasksFormTests(TestCase):
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

