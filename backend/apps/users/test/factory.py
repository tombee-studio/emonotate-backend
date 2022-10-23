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


class EnqueteFactory(django.DjangoModelFactory):
    class Meta:
        model = Enquete
    
    title = factory.Faker('word')
    description = factory.Faker('sentence')


class CurveFactory(django.DjangoModelFactory):
    class Meta:
        model = Curve
    
    user = factory.SubFactory(EmailUserFactory)
    content = factory.SubFactory(ContentFactory)
    value_type = factory.SubFactory(ValueTypeFactory)
    values = json.dumps([])
    version = '1.1.0'
    room_name = factory.Faker("word")

    @factory.post_generation
    def answers(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for [enquete, item] in extracted:
                self.enquete.add(enquete)
                answer = self.enqueteanswer_set.get(enquete=enquete)
                answer.answer = item.answer
                answer.save()


class EnqueteAnswerFactory(django.DjangoModelFactory):
    class Meta: 
        model = EnqueteAnswer
    
    curve = factory.SubFactory(CurveFactory)
    enquete = factory.SubFactory(EnqueteFactory)
    answer = factory.Faker('sentence')


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
    
    @factory.post_generation
    def enquetes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for enquete in extracted:
                self.enquetes.add(enquete)
