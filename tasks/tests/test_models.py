from django.contrib.auth.models import User
from django.test import TestCase

from tasks.models import Task, TaskChange, UserSettings


class TaskModelTests(TestCase):
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


class TaskChangeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

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


class UserSettingsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_create_user_settings(self):
        user_settings = UserSettings.objects.create(
            user=self.user,
            send_report=True,
            report_time="00:00:00",
        )
        self.assertEqual(str(user_settings), "testuser's settings")
        self.assertTrue(UserSettings.objects.filter(user=self.user).exists())

    def test_update_report_time(self):
        user_settings = UserSettings.objects.create(
            user=self.user,
            send_report=True,
            report_time="00:00:00",
        )
        user_settings.report_time = "12:00:00"
        user_settings.save()
        self.assertEqual(str(user_settings), "testuser's settings")
        self.assertTrue(UserSettings.objects.filter(user=self.user).exists())
