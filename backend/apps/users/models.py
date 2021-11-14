from __future__ import unicode_literals

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group

import random
import string


def randomname(n=6):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)


class EmailUserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser,
                     **extra_fields):
        now = timezone.now()

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        is_active = extra_fields.pop("is_active", True)

        user = self.model(
            username=username,
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
    
    def create_unique_user(self, email, is_test=False):
        username = randomname()
        while True:
            try:
                EmailUser.objects.get(username=username)
            except:
                break
            username = randomname()
        if not is_test:
            user = EmailUser.objects.create_user(
                username=username, 
                email=email,
                password="password")
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        is_staff = extra_fields.pop("is_staff", False)
        user = self._create_user(
            username,
            email,
            password,
            is_staff,
            False,
            **extra_fields
        )
        try:
            group = Group.objects.get(name='General')
        except Group.DoesNotExist:
            print("Does not exists")
        else:
            user.groups.add(group)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(
            username,
            email, password,
            True,
            True,
            **extra_fields
        )


class EmailUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        unique=True, 
        max_length=32, 
        default=randomname(8))

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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.email

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return '%s(%s)' % (self.username, self.email)
    
    def __str__(self):
        return f"{self.id}: {self.username}({self.email})"


class ValueType(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(EmailUser, default=1, on_delete=models.CASCADE)
    title = models.CharField(default='', max_length=256)
    axis_type = models.IntegerField(choices=(
        (1, '平常状態を含んで上と下がある値'),
        (2, '平常状態から上にしか上がらない値')), default=1)

    def __str__(self):
        return self.title


class Content(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(EmailUser, default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    url = models.URLField(default='', max_length=1024)
    data_type = models.CharField(default='video/mp4', max_length=32)

    def __str__(self):
        return self.title


class Curve(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(EmailUser,
                             default=1,
                             on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.PROTECT)
    value_type = models.ForeignKey(ValueType, default=1, on_delete=models.CASCADE)
    values = JSONField()
    version = models.CharField(max_length=16)
    room_name = models.CharField(max_length=32, default="")
    locked = models.BooleanField(default=True)

    def __str__(self):
        return '{} {}'.format(self.content.title, self.id)


class Questionaire(models.Model):
    url = models.URLField(default="")
    user_id_form = models.CharField(max_length=32)

class Request(models.Model):
    room_name = models.CharField(max_length=6, null=True, blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128, default="")
    description = models.TextField(blank=False, default="")
    owner = models.ForeignKey(EmailUser, 
                              default=1,
                              on_delete=models.CASCADE, 
                              related_name='owner')
    participants = models.ManyToManyField(EmailUser)
    intervals = models.IntegerField(default=1)
    content = models.ForeignKey(
        Content, 
        default=1,
        on_delete=models.CASCADE)
    value_type = models.ForeignKey(
        ValueType,
        default=1,
        on_delete=models.CASCADE
    )
    questionaire = models.ForeignKey(Questionaire, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL, 
        default=None)

    def save(self, **kwargs):
        if not self.room_name:
            self.room_name = randomname()
            while Request.objects.filter(room_name=self.room_name).exists():
                self.room_name = randomname()
        super(Request, self).save(**kwargs)
    
    def __str__(self):
        return f'{self.title}({self.room_name})'
