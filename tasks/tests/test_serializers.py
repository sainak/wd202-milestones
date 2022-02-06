from django.contrib.auth.models import User
from django.test import TestCase

from tasks.models import Task
from tasks.serializers import TaskChangeSerializer, TaskSerializer


class TaskSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_create_task(self):
        task = TaskSerializer(
            data={
                "title": "test title 1",
                "description": "test description",
                "priority": 1,
                "status": "PENDING",
            }
        )
        self.assertTrue(task.is_valid())
        task.save(owner=self.user)
        self.assertTrue(
            Task.objects.filter(owner=self.user, title="test title 1").exists()
        )
        self.assertEqual(str(task.data["title"]), "test title 1")

    def test_task_priority_increment(self):
        Task.objects.create(
            title="test title 1",
            description="test description",
            priority=3,
            owner=self.user,
        )
        task1 = TaskSerializer(
            data={
                "title": "test title 2",
                "description": "test description",
                "priority": 1,
                "status": "PENDING",
            }
        )
        self.assertTrue(task1.is_valid())
        task1.save(owner=self.user)
        task2 = TaskSerializer(
            data={
                "title": "test title 3",
                "description": "test description",
                "priority": 1,
                "status": "PENDING",
            }
        )
        self.assertTrue(task2.is_valid())
        task2.save(owner=self.user)
        task1 = Task.objects.get(pk=task1.instance.pk)
        self.assertEqual(task1.priority, 2)


class TaskChangeSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_create_task_change(self):
        task = Task.objects.create(
            title="test title 1",
            description="test description",
            priority=1,
            owner=self.user,
        )
        task.status = "COMPLETED"
        task.save()
        task.status = "IN_PROGRESS"
        task.save()
        task_change = TaskChangeSerializer(task.changes.all(), many=True)
        self.assertEqual(len(task_change.data), 2)
