from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User


class YourTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_viewer = User.objects.create_user(
            username="john", email="viewer@example.com", password="johnpass", role="viewer"
        )
        self.user_annotator = User.objects.create_user(
            username="marie", email="annotator@example.com", password="mariepass", role="annotator"
        )
        self.user_reviewer = User.objects.create_user(
            username="alice", email="reviewer@example.com", password="alicepass", role="reviewer"
        )


def test_create_annotation_annotator(self):
    self.client.login(username="marie", password="mariepass")
    # Make a request to the create_annotation view
    response = self.client.get("create/")
    # Assert that the response status code is 200 (OK)
    self.assertEqual(response.status_code, 200)


def test_create_annotation_reviewer(self):
    self.client.login(username="alice", password="alicepass")
    # Make a request to the create_annotation view
    response = self.client.get("create/")
    # Assert that the response status code is 200 (OK)
    self.assertEqual(response.status_code, 200)


def test_create_annotation_viewer(self):
    self.client.login(username="john", password="johnpass")
    # Make a request to the create_annotation view
    response = self.client.get("create/")
    # Assert that the response status code is 200 (OK)
    self.assertEqual(response.status_code, 200)  # change to error message or status code  ff
