from faker import Faker as FakerClass
from typing import Any, Sequence
from factory import django, Faker, post_generation

from users.models import EmailUser


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
