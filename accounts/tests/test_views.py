from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.views import UserLoginView, UserSignupView


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_get_login_view(self):
        request = self.factory.get(reverse("login"))
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_post_login_view_csrf_error(self):
        request = self.factory.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "testpassword",
            },
        )
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 403)


class UserSignupViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_signup_view(self):
        request = self.factory.get(reverse("signup"))
        response = UserSignupView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_post_signup_view(self):
        request = self.factory.post(
            reverse("signup"),
            {
                "username": "testuser",
                "email": "test@test.com",
                "password1": "testpassword",
                "password2": "testpassword",
            },
        )
        response = UserSignupView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())
