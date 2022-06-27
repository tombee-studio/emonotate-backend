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

from backend.settings.common import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_URL

import boto3


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
