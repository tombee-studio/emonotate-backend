from faker import Faker as FakerClass
from typing import Any, Sequence
from factory import django

from users.models import *
from django.utils import timezone

import factory
import json

class EmailUserFactory(django.DjangoModelFactory):
    class Meta:
        model = EmailUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')

    @factory.post_generation
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
    title = factory.Faker('word')
    url = factory.Faker('url')


class YouTubeContentFactory(django.DjangoModelFactory):
    class Meta:
        model = YouTubeContent

    user = factory.SubFactory(EmailUserFactory)
    title = factory.Faker('word')
    url = factory.Faker('url')
    video_id = factory.Faker('name')


class ValueTypeFactory(django.DjangoModelFactory):
    class Meta:
        model = ValueType

    user = factory.SubFactory(EmailUserFactory)
    title = factory.Faker('word')
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


class RequestFactory(django.DjangoModelFactory):
    class Meta:
        model = Request
    
    owner = factory.SubFactory(EmailUserFactory)
    content = factory.SubFactory(ContentFactory)
    value_type = factory.SubFactory(ValueTypeFactory)
    
    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for participant in extracted:
                self.participants.add(participant)
