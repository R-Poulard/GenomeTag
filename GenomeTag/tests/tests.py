from django.test import TestCase
from ..views import create
from django.test import Client
from django.contrib.auth.models import User

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

class YourTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        # Create users with random passwords
        self.user_viewer = User.objects.create_user(username="john", email="viewer@example.com", password=make_password(None), role="viewer")
        self.user_annotator = User.objects.create_user(username="marie", email="annotator@example.com", password=make_password(None), role="annotator")
        self.user_reviewer = User.objects.create_user(username="alice", email="reviewer@example.com", password=make_password(None), role="reviewer")

    def test_create_annotation_annotator(self):
        self.client.login(username="marie")

            # Get the URL for the create_annotation view using reverse
        create_annotation_url = reverse('GenomeTag:create')  # Replace 'create_annotation' with the actual name or URL pattern name of your view

            # Make a request to the create_annotation view
        response = self.client.get(create_annotation_url)

            # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)


    def test_create_annotation_reviewer(self):
        self.client.login(username="alice")
        # Make a request to the create_annotation view
        response = self.client.get('GenomeTag:create') 
        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_create_annotation_viewer(self):
        self.client.login(username="john")
        # Make a request to the create_annotation view
        response = self.client.get('GenomeTag:create') 
        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200) # change to error message or status code 

