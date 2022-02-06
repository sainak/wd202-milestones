from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException


class UserSeleniumTests(StaticLiveServerTestCase):
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
