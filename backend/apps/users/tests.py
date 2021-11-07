from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.test.factory import *
from users.models import EmailUser
from faker import Faker

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
            'password1': 'test_Pass',
            'password2': 'test_Pass',
            'email': self.user_object.email,
        }
        response = self.client.post(self.signup_url, signup_dict)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(EmailUser.objects.count(), 2)

    def test_if_username_already_exists_dont_signup(self):
        # Prepare data with already saved user
        signup_dict = {
            'username': self.user_saved.username,
            'password1': 'test_Pass',
            'password2': 'test_Pass',
            'email': self.user_saved.email,
        }
        response = self.client.post(self.signup_url, signup_dict)


class ContentAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.content_obj = ContentFactory.build()
        cls.client = APIClient()
        cls.url = reverse('contents')
        cls.faker_obj = Faker()
    
    def test_api_is_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
