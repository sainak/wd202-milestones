from django.contrib.auth.models import User
from django.test import TestCase

from accounts.forms import AuthenticationForm, UserCreationForm


class UserSignupFormTest(TestCase):
    def test_valid_form(self):
        form = UserCreationForm(
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password1": "testpassword",
                "password2": "testpassword",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_email_form(self):
        form = UserCreationForm(
            data={
                "username": "testuser",
                "email": "invalid_email",
                "password1": "testpassword",
                "password2": "testpassword",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["Enter a valid email address."])

    def test_invalid_password_form(self):
        form = UserCreationForm(
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password1": "testpassword",
                "password2": "invalid_password",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password2"], ["The two password fields didn’t match."]
        )


class UserLoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def test_valid_form(self):
        form = AuthenticationForm(
            data={
                "username": "testuser",
                "password": "testpassword",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = AuthenticationForm(
            data={
                "username": "invalid_user",
                "password": "invalid_password",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"],
            [
                "Please enter a correct username and password. Note that both "
                "fields may be case-sensitive."
            ],
        )
