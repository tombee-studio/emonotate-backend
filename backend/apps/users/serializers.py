from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    def to_internal_value(self, address):
        return User.objects.get(email=address)


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


class YouTubeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeContent
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
        try:
            c = Content.objects.get(pk=ret['content'])
            youtube = YouTubeContent.objects.get(pk=c.youtubecontent)
            ret['content'] = YouTubeContentSerializer(youtube).data
        except Content.youtubecontent.RelatedObjectDoesNotExist:
            ret['content'] = ContentSerializer(c).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        return ret


class QuestionaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionaire
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['owner'] = UserSerializer(User.objects.get(pk=ret['owner'])).data
        ret['content'] = ContentSerializer(Content.objects.get(pk=ret['content'])).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        ret['participants'] = [User.objects.get(pk=pk).email for pk in ret['participants']]
        if ret['questionaire'] != None:
            ret['questionaire'] = QuestionaireSerializer(Questionaire.objects.get(pk=ret['questionaire'])).data
        return ret
    
    def create(self, validated_data):
        instance = Request.objects.create(
            content=validated_data['content'],
            owner=validated_data['owner'],
            value_type=validated_data['value_type'],
            title=validated_data['title'],
            description=validated_data['description']
        )
        instance.participants.set(validated_data['participants'])
        return instance
