from django.contrib.auth.models import User
from django.test import TestCase


class UserModelTest(TestCase):
    def test_create_user(self):
        User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        self.assertTrue(User.objects.filter(username="testuser").exists())
