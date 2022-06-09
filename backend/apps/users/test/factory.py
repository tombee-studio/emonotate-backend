from faker import Faker as FakerClass
from typing import Any, Sequence
from factory import django, Faker, post_generation

from users.models import *
from django.utils import timezone

import factory
import json

class EmailUserFactory(django.DjangoModelFactory):
    class Meta:
        model = EmailUser

    username = Faker('user_name')
    email = Faker('email')

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else FakerClass().password(
                length=30,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            )
        )
        self.set_password(password)


class ContentFactory(django.DjangoModelFactory):
    class Meta:
        model = Content

    user = factory.SubFactory(EmailUserFactory)
    title = Faker('word')
    url = Faker('url')


class YouTubeContentFactory(django.DjangoModelFactory):
    class Meta:
        model = YouTubeContent

    user = factory.SubFactory(EmailUserFactory)
    title = Faker('word')
    url = Faker('url')
    video_id = Faker('name')


class ValueTypeFactory(django.DjangoModelFactory):
    class Meta:
        model = ValueType

    user = factory.SubFactory(EmailUserFactory)
    title = Faker('word')
    axis_type = 1


class CurveFactory(django.DjangoModelFactory):
    class Meta:
        model = Curve
    
    user = factory.SubFactory(EmailUserFactory)
    content = factory.SubFactory(ContentFactory)
    value_type = factory.SubFactory(ValueTypeFactory)
    values = json.dumps([])
    version = '1.1.0'
    room_name = ""
