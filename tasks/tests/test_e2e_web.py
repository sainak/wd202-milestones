from datetime import time

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException

from tasks.models import Task, UserSettings


class TasksSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            options = webdriver.ChromeOptions()
            # options.add_argument("--headless")
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

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def send_keys(self, element, keys):
        self.selenium.find_element_by_id(element).clear()
        self.selenium.find_element_by_id(element).send_keys(keys)

    def login(self):
        self.selenium.get(self.live_server_url + reverse("login"))
        self.send_keys("id_username", "testuser")
        self.send_keys("id_password", "testpassword")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    def test_create_task(self):
        self.login()

        self.selenium.get(self.live_server_url + reverse("tasks-create"))
        self.send_keys("id_title", "test task")
        self.send_keys("id_description", "test description")
        self.send_keys("id_priority", "1")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        self.assertEqual(
            self.selenium.current_url, self.live_server_url + reverse("tasks-list")
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div/div/div[1]/a"
            ).text,
            "test task",
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div/h1"
            ).text,
            "1",
        )

    def test_task_details(self):
        self.login()

        task = Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        self.selenium.get(self.live_server_url + reverse("tasks-list"))
        self.selenium.find_element_by_xpath(
            "/html/body/div/div[2]/div/div/div/div[1]/a"
        ).click()
        self.assertEqual(
            self.selenium.find_element_by_xpath("/html/body/div/div[2]/div/h1[1]").text,
            task.title,
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath("/html/body/div/div[2]/div/p").text,
            task.description,
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath("/html/body/div/div[2]/div/h1[2]").text,
            task.status,
        )

    def test_update_task(self):
        self.login()

        Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )
        self.selenium.get(self.live_server_url + reverse("tasks-list"))
        self.selenium.find_element_by_xpath(
            "/html/body/div/div[2]/div/div/a[1]"
        ).click()
        self.send_keys("id_title", "test task updated")
        self.send_keys("id_priority", "2")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        self.assertEqual(
            self.selenium.current_url, self.live_server_url + reverse("tasks-list")
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div/div/div[1]/a"
            ).text,
            "test task updated",
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div/h1"
            ).text,
            "2",
        )

    def test_task_priority_increment(self):
        self.login()

        self.selenium.get(self.live_server_url + reverse("tasks-create"))
        self.send_keys("id_title", "test task")
        self.send_keys("id_description", "test description")
        self.send_keys("id_priority", "1")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.selenium.get(self.live_server_url + reverse("tasks-create"))
        self.send_keys("id_title", "test task 2")
        self.send_keys("id_description", "test description 2")
        self.send_keys("id_priority", "1")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.selenium.get(self.live_server_url + reverse("tasks-list"))
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/h1"
            ).text,
            "2",
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/div/div[1]/a"
            ).text,
            "test task",
        )

    def test_task_priority_does_not_increment(self):
        self.login()

        self.selenium.get(self.live_server_url + reverse("tasks-create"))
        self.send_keys("id_title", "test task")
        self.send_keys("id_description", "test description")
        self.send_keys("id_priority", "1")
        self.selenium.find_element_by_xpath(
            '//select[@id="id_status"]/option[@value="COMPLETED"]'
        ).click()
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.selenium.get(self.live_server_url + reverse("tasks-create"))
        self.send_keys("id_title", "test task 2")
        self.send_keys("id_description", "test description 2")
        self.send_keys("id_priority", "1")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.selenium.get(self.live_server_url + reverse("tasks-list"))
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/h1"
            ).text,
            "1",
        )
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/div/div[1]/a"
            ).text,
            "test task",
        )

    def test_delete_task(self):
        Task.objects.create(
            title="Test Task",
            owner=self.user,
            description="Test Description",
            priority=1,
        )

        self.login()
        self.selenium.find_element_by_xpath(
            "/html/body/div/div[2]/div/div/a[2]"
        ).click()
        self.selenium.find_element_by_xpath("/html/body/form/div/div[2]/button").click()

        self.assertEqual(Task.objects.count(), 0)


class UserSettingsSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            options = webdriver.ChromeOptions()
            # options.add_argument("--headless")
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

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )

    def send_keys(self, element, keys):
        self.selenium.find_element_by_id(element).clear()
        self.selenium.find_element_by_id(element).send_keys(keys)

    def login(self):
        self.selenium.get(self.live_server_url + reverse("login"))
        self.send_keys("id_username", "testuser")
        self.send_keys("id_password", "testpassword")
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    def test_user_settings_update(self):
        self.login()

        self.selenium.get(self.live_server_url + reverse("user-settings"))

        self.selenium.find_element_by_id("id_send_report").click()
        self.send_keys("id_report_time", "11:00")

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.assertEqual(
            UserSettings.objects.get(user=self.user).report_time, time(11, 0, 0)
        )
