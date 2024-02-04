from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings


class UsersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.expected_domain = getattr(settings, "EMAIL_DOMAIN")
        self.user_credentials = {
            "username": "testuser",
            "email": f"user@{self.expected_domain}",
            "password": "testpassword",
        }

    def test_signup_valid_email(self):
        email = f"test_signup@{self.expected_domain}"
        username = "test_signup"
        password = "testpassword"

        response = self.client.post(
            reverse("signup"),
            {
                "username": username,
                "email": email,
                "password1": password,
                "password2": password,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("batch_list"))
        self.assertTrue(User.objects.filter(email=email).exists())

    def test_signup_invalid_email(self):
        email = "invalid@test.com"
        username = "test_signup"
        password = "testpassword"

        response = self.client.post(
            reverse("signup"),
            {
                "username": username,
                "email": email,
                "password1": password,
                "password2": password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"Email must end with {self.expected_domain}", response.content.decode()
        )

    def test_login(self):
        User.objects.create_user(**self.user_credentials)

        response = self.client.post(
            reverse("login"),
            {
                "username": self.user_credentials["username"],
                "password": self.user_credentials["password"],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("batch_list"))
        user = User.objects.get(username=self.user_credentials["username"])
        self.assertTrue(user.is_authenticated)
