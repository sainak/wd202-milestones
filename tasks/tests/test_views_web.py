from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from tasks.models import Task
from tasks.views.web import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskHistoryView,
    TaskListView,
    TaskUpdateView,
    UserSettingsView,
)


class TaskViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_task_list_view(self):
        Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.get(reverse("tasks-list"))
        request.user = self.user
        response = TaskListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["tasks"].count(), 1)

    def test_get_task_detail_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.get(reverse("tasks-detail", args=(task.id,)))
        request.user = self.user
        response = TaskDetailView.as_view()(request, pk=task.id)
        self.assertEqual(response.status_code, 200)

    def test_get_task_create_view(self):
        request = self.factory.get(reverse("tasks-create"))
        request.user = self.user
        response = TaskCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_task_update_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.get(reverse("tasks-update", args=(task.id,)))
        request.user = self.user
        response = TaskUpdateView.as_view()(request, pk=task.id)
        self.assertEqual(response.status_code, 200)

    def test_get_task_delete_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.get(reverse("tasks-delete", args=(task.id,)))
        request.user = self.user
        response = TaskDeleteView.as_view()(request, pk=task.id)
        self.assertEqual(response.status_code, 200)


class TaskHistoryViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_task_history_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        task.status = "COMPLETED"
        task.save()
        task.status = "IN_PROGRESS"
        task.save()
        request = self.factory.get(reverse("tasks-history", args=(task.id,)))
        request.user = self.user
        response = TaskHistoryView.as_view()(request, pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["task"].id, task.id)


class UserSettingsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_user_settings_view(self):
        request = self.factory.get(reverse("user-settings"))
        request.user = self.user
        response = UserSettingsView.as_view()(request)
        self.assertEqual(response.status_code, 200)
