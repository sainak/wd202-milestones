from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from tasks.models import Task, UserSettings


class TaskIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_task_list(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=0,
            status="PENDING",
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tasks"][0], task)

    def test_task_detail(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=0,
            status="PENDING",
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("tasks-detail", kwargs={"pk": task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], task)

    def test_task_history(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=0,
            status="PENDING",
        )
        task.status = "COMPLETED"
        task.save()
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("tasks-history", kwargs={"pk": task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], task)
        self.assertEqual(len(response.context["task_changes"]), 1)

    def test_create_task(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("tasks-create"),
            {
                "title": "Test Task",
                "description": "Test Description",
                "priority": 0,
                "status": "PENDING",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)

    def test_update_task(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=0,
            status="PENDING",
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("tasks-update", kwargs={"pk": task.pk}),
            {
                "title": "Test Task",
                "description": "Test Description",
                "priority": 1,
                "status": "PENDING",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=task.pk).priority, 1)

    def test_delete_task(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=0,
            status="PENDING",
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("tasks-delete", kwargs={"pk": task.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 0)


class UserSettingsIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_user_settings(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("user-settings"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["object"], UserSettings.objects.get(user=self.user)
        )
