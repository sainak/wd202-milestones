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

    def test_get_task_list_view(self):
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

    def test_get_task_detail_view(self):
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
