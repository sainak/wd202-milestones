from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from tasks.models import Task
from tasks.views.api import TaskChangeViewSet, TaskViewSet


class TaskApiViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
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
        request = self.factory.get(reverse("api-task-list"))
        request.user = self.user
        response = TaskViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_post_task_view(self):
        request = self.factory.post(
            reverse("api-task-list"),
            {
                "title": "Test Task",
                "description": "Test Description",
                "priority": 1,
                "status": "PENDING",
            },
        )
        request.user = self.user
        response = TaskViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)

    def test_get_task_detail_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.get(reverse("api-task-detail", args=[task.id]))
        request.user = self.user
        response = TaskViewSet.as_view({"get": "retrieve"})(request, pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], task.id)

    def test_put_task_detail_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.put(
            reverse("api-task-detail", args=[task.id]),
            {
                "title": "Test Task Updated",
                "description": "Test Description",
                "priority": 1,
                "status": "PENDING",
            },
        )
        request.user = self.user
        response = TaskViewSet.as_view({"put": "update"})(request, pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], task.id)
        self.assertEqual(response.data["title"], "Test Task Updated")

    def test_patch_task_detail_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.patch(
            reverse("api-task-detail", args=[task.id]),
            {"title": "Test Task Updated"},
        )
        request.user = self.user
        response = TaskViewSet.as_view({"patch": "partial_update"})(request, pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], task.id)
        self.assertEqual(response.data["title"], "Test Task Updated")

    def test_delete_task_detail_view(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            owner=self.user,
            priority=1,
        )
        request = self.factory.delete(reverse("api-task-detail", args=[task.id]))
        request.user = self.user
        response = TaskViewSet.as_view({"delete": "destroy"})(request, pk=task.id)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.count(), 0)


class TaskChangeApiViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_task_change_list_view(self):
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
        request = self.factory.get(reverse("api-task-history-list", args=[task.id]))
        request.user = self.user
        response = TaskChangeViewSet.as_view({"get": "list"})(request, task_pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_filtered_task_change_list_view(self):
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
        request = self.factory.get(
            f"{reverse('api-task-history-list', args=[task.id])}?new_status=COMPLETED",
        )
        request.user = self.user
        response = TaskChangeViewSet.as_view({"get": "list"})(request, task_pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["new_status"], "COMPLETED")
