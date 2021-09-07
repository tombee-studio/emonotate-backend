from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ValueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueType
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(User.objects.get(pk=ret['user'])).data
        return ret


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(User.objects.get(pk=ret['user'])).data
        return ret


class CurveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curve
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(User.objects.get(pk=ret['user'])).data
        ret['content'] = ContentSerializer(Content.objects.get(pk=ret['content'])).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        return ret
