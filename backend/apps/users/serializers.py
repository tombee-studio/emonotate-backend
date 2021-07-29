from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'last_login',
            'is_active', 'date_joined', 'last_updated'
        )


class ValueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueType


class ContentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Content


class CurveSerializer(serializers.ModelSerializer):
    content = ContentSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    value_type = ValueTypeSerializer(read_only=True)

    class Meta:
        model = Curve
