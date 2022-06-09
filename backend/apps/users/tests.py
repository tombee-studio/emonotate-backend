import factory
import json
import random

from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.test.factory import *
from users.models import *
from users.views import *
from faker import Faker
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory, force_authenticate

from users import views

from rest_framework.renderers import JSONRenderer


def convert_to_dict_from(model):
    data = { key: value if type(value) is str or type(value) is int else str(value)
        for key, value in model.__dict__.items() if key is not '_state' and value is not None }
    return data


def createTestData():
    for name, perms in [
        ('Guest', 
         ['view_request', 'view_content', 'view_valuetype', 
          'add_youtubecontent', 'view_youtubecontent', 
          'view_emailuser', 'view_curve', 'add_curve']), 
        ('General', 
         ['view_request',       'add_request',      'change_request', 'delete_request', 
          'view_content',       'add_content',      'change_content', 'delete_content',
          'view_valuetype',     'add_valuetype',    'change_valuetype', 'delete_valuetype',
          'view_youtubecontent','add_youtubecontent', 'change_youtubecontent', 'delete_youtubecontent',
          'view_emailuser',     'add_emailuser',    'change_emailuser', 'delete_emailuser',
          'view_curve',         'add_curve',    'change_curve', 'delete_curve']),
        ('Researchers', 
         ['view_request',       'add_request',      'change_request', 'delete_request', 
          'view_content',       'add_content',      'change_content', 'delete_content',
          'view_valuetype',     'add_valuetype',    'change_valuetype', 'delete_valuetype',
          'view_youtubecontent','add_youtubecontent', 'change_youtubecontent', 'delete_youtubecontent',
          'view_emailuser',     'add_emailuser',    'change_emailuser', 'delete_emailuser',
          'view_curve',         'add_curve',    'change_curve', 'delete_curve'])]:
        group = Group.objects.create(name=name)
        for perm in perms:
            group.permissions.add(Permission.objects.get(codename=perm))
    User.objects.create_superuser("tomoya", "tomoya@example.com", "youluck123")
    User.objects.create_guest_user("guest")
    User.objects.create_unique_user("general@example.com", username="general")
    User.objects.create_researcher("researcher", "researcher@example.com", "password")
    ContentFactory.create()
    ValueTypeFactory.create()


class CurveWithYouTubeSerializerTest(TestCase):
    def setUp(self):
        createTestData()

    def test_serialize_curve(self):
        faker = Faker()
        user = EmailUser.objects.create_user(
            username=faker.name(), email=faker.email(), password=faker.password())
        content = YouTubeContentFactory.create(video_id=randomname())
        value_type = ValueTypeFactory.create()
        obj = CurveFactory.build(
            user=user, content=content, value_type=value_type, room_name=randomname())
        serializer = CurveWithYouTubeSerializer(obj)
        self.assertEqual(len(Content.objects.all()), 2)
        self.assertEqual(len(YouTubeContent.objects.all()), 1)
        s = CurveWithYouTubeSerializer(data={
            "values": [],
            "version": "1.0.1",
            "room_name": "aaaaaaa",
            "locked": False,
            "user": 1,
            "youtube": {
                "user": 1,
                "title": "Hello, World!",
                "url": "https://www.youtube.com/watch?v=QOpl7cI8ubU",
                "video_id": "QOpl7cI8ubU"
            },
            "value_type": {
                "user": 1,
                "title": "面白さ",
                "axis_type": 1
            }
        })
        self.assertEqual(s.is_valid(), True)


class EmailUserTestCase(TestCase):
    def setUp(self):
        createTestData()

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
    def setUp(cls):
        createTestData()
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
