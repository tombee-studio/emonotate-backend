import factory
import json
import random

from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.test.factory import *
from users.models import EmailUser
from faker import Faker
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from users import views


class EmailUserTestCase(TestCase):
    def test_create_generaluser(self):
        faker = Faker()
        username = faker.name()
        email = faker.email()
        user = EmailUser.objects.create_user(
            username=username, email=email, password=faker.password())
        self.assertEqual(user.username, username)
        for perm in ['users.add_request', 'users.add_content', 'users.add_emailuser']:
            self.assertEqual(user.has_perm(perm), False)
    
    def test_create_researcher(self):
        faker = Faker()
        username = faker.name()
        email = faker.email()
        user = EmailUser.objects.create_researcher(
            username=username, email=email, password=faker.password())
        self.assertEqual(user.username, username)
        for perm in ['users.add_request', 'users.add_content', 'users.add_emailuser']:
            self.assertEqual(user.has_perm(perm), True)
        

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


class YouTubeContentAPITestCase(APITestCase):
    def test_get_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 200],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            client.login(username=username, password=password)
            url = '/api/youtube/'
            response = client.get(url)
            self.assertEqual(response.status_code, status)
    
    def test_post_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            client.login(username=username, password=password)
            url = '/api/youtube/'
            response = client.post(url, json.dumps({
                "title": Faker().word(),
                "url": Faker().url(),
                "video_id": Faker().word(),
                "channel_title": Faker().word(),
                "user": EmailUser.objects.get(username=username).id
            }), content_type="application/json")
            self.assertEqual(response.status_code, status)
    
    def test_put_api(self):
        client = APIClient()
        video_id = Faker().word()
        content = YouTubeContent.objects.create(
            title=Faker().word(),
            url=Faker().url(),
            video_id=video_id,
            channel_title=Faker().word(),
            user=EmailUser.objects.get(username='tomoya')
        )
        content.save()
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            client.login(username=username, password=password)
            url = '/api/youtube/' + str(content.id) + '/'
            response = client.put(url, json.dumps({
                "id": content.id,
                "title": Faker().word(),
                "url": Faker().url(),
                "video_id": video_id,
                "channel_title": Faker().word(),
                "user": EmailUser.objects.get(username=username).id
            }), content_type="application/json")
            self.assertEqual(response.status_code, status)

    def test_put_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            content = YouTubeContent.objects.create(
                title=Faker().word(),
                url=Faker().url(),
                video_id=Faker().word(),
                channel_title=Faker().word(),
                user=EmailUser.objects.get(username='tomoya')
            )
            content.save()
            client.login(username=username, password=password)
            url = '/api/youtube/' + str(content.id) + '/'
            response = client.delete(url)
            self.assertEqual(response.status_code, status)

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

        response = client.put(url + "103/", json.dumps({
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
        self.assertEqual(response.status_code, 200)

        response = client.put(url + "103/", json.dumps({
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
        self.assertEqual(response.status_code, 200)

        response = client.put(url + "103/", json.dumps({
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
        self.assertEqual(response.status_code, 200)
    
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
