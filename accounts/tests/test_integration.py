from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class UserSignupIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_can_signup(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "email": "test@test.com",
                "password1": "testpassword",
                "password2": "testpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))


class UserLoginIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_user_can_login_and_logout(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
