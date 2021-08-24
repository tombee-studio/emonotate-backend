from __future__ import unicode_literals

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

import random
import string


def randomname(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)


class EmailUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser,
                     **extra_fields):
        now = timezone.now()

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        is_active = extra_fields.pop("is_active", True)

        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        is_staff = extra_fields.pop("is_staff", False)

        return self._create_user(
            email,
            password,
            is_staff,
            False,
            **extra_fields
        )

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(
            email, password,
            True,
            True,
            **extra_fields
        )


class EmailUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=32, default=randomname(8))

    email = models.EmailField(
        max_length=256,
        unique=True,
        error_messages={
            'unique': 'That email address is already taken.'
        }
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        permissions = (
            ('view_emailuser', 'Can view email users'),
        )

    def __unicode__(self):
        return self.email

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return '%s(%s)' % (self.username, self.email)


class ValueType(models.Model):
    user = models.ForeignKey(EmailUser, default=1, on_delete=models.CASCADE)
    title = models.CharField(default='', max_length=256)
    axis_type = models.IntegerField(choices=(
        (1, '平常状態を含んで上と下がある値'),
        (2, '平常状態から上にしか上がらない値')), default=1)

    def __str__(self):
        return self.title


class Content(models.Model):
    user = models.ForeignKey(EmailUser, default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    url = models.URLField(default='', max_length=1024)
    data_type = models.CharField(default='video/mp4', max_length=32)

    def __str__(self):
        return self.title


class Curve(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(EmailUser,
                             default=1,
                             on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.PROTECT)
    value_type = models.ForeignKey(ValueType, default=1, on_delete=models.CASCADE)
    values = JSONField()
    version = models.CharField(max_length=16)

    def __str__(self):
        return '{} {}'.format(self.content.title, self.id)

