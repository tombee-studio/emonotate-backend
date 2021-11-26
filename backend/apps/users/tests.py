import factory
import json
import random

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.test.factory import *
from users.models import EmailUser
from faker import Faker
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from users import views

class EmailUserSignUpTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_object = EmailUserFactory.build()
        cls.user_saved = EmailUserFactory.create()
        cls.client = APIClient()
        cls.signup_url = reverse('signup')
        cls.faker_obj = Faker()

    def test_if_data_is_correct_then_signup(self):
        signup_dict = {
            'username': self.user_object.username,
            'password1': 'password',
            'password2': 'password',
            'email': self.user_object.email,
        }
        response = self.client.post(self.signup_url, signup_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_username_already_exists_dont_signup(self):
        # Prepare data with already saved user
        signup_dict = {
            'username': self.user_saved.username,
            'password1': 'password',
            'password2': 'password',
            'email': self.user_saved.email,
        }
        response = self.client.post(self.signup_url, signup_dict)


class ContentAPITestCase(APITestCase):
    def test_api_superuser(self):
        client = APIClient()
        client.login(username='tomoya', password='youluck123')
        url = '/api/contents/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)


class RequestAPITestCase(APITestCase):
    def test_api_superuser(self):
        client = APIClient()
        client.login(username='tomoya', password='youluck123')
        url = '/api/requests/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
    
    def test_api_generaluser(self):
        client = APIClient()
        client.login(username='general', password='password')
        url = '/api/requests/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="general").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 403)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="general").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 403)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="general").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 403)
    

    def test_api_researcher(self):
        USERNAME = "researcher"
        client = APIClient()
        client.login(username=USERNAME, password='password')
        url = '/api/requests/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username=USERNAME).id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username=USERNAME).id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username=USERNAME).id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
