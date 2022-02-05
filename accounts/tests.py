from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException

from .forms import AuthenticationForm, UserCreationForm


class UserModelTest(TestCase):
    def test_create_user(self):
        User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        assert User.objects.filter(username="testuser").exists()


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


class UserClientTest(TestCase):
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

    def test_user_can_login(self):
        User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_user_can_logout(self):
        User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))


class UserModelSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            cls.selenium = webdriver.Chrome(options=options)
        except SessionNotCreatedException:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def send_keys_to_element(self, element, keys):
        self.selenium.find_element_by_id(element).send_keys(keys)

    def test_user_can_signup(self):
        self.selenium.get(self.live_server_url + reverse("signup"))
        self.send_keys_to_element("id_username", "testuser")
        self.send_keys_to_element("id_email", "test@test.com")
        self.send_keys_to_element("id_password1", "testpassword")
        self.send_keys_to_element("id_password2", "testpassword")

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.assertEqual(
            self.selenium.current_url, self.live_server_url + reverse("login")
        )
        self.assertEqual(User.objects.get(username="testuser").email, "test@test.com")

    def test_user_can_login(self):
        User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        self.selenium.get(self.live_server_url + reverse("login"))
        self.send_keys_to_element("id_username", "testuser")
        self.send_keys_to_element("id_password", "testpassword")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.assertEqual(
            self.selenium.current_url, self.live_server_url + reverse("tasks-list")
        )

    def test_user_can_logout(self):
        User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        self.selenium.get(self.live_server_url + reverse("login"))
        self.send_keys_to_element("id_username", "testuser")
        self.send_keys_to_element("id_password", "testpassword")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.selenium.find_element_by_xpath(f'//a[@href="{reverse("logout")}"]').click()

        self.assertEqual(
            self.selenium.current_url, self.live_server_url + reverse("login")
        )
