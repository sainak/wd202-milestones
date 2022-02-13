from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from tasks.models import Task


class TaskApiIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_task_list(self):
        Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("api-task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_task_detail(self):
        Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("api-task-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Task")

    def test_create_new_task(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("api-task-list"),
            {
                "title": "Test Task",
                "description": "Test Description",
                "priority": 1,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)

    def test_update_task(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.put(
            reverse("api-task-detail", kwargs={"pk": task.pk}),
            {"title": "Updated Task"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Task")

    def test_delete_task(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.delete(
            reverse("api-task-detail", kwargs={"pk": task.pk})
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.count(), 0)


class TaskHistoryApiIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_task_history(self):
        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        task.status = "COMPLETED"
        task.save()
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse("api-task-history-list", kwargs={"task_pk": 1})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
