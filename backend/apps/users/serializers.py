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
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["groups"] = [group.name for group in instance.groups.all()]
        return ret


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
        try:
            c = Content.objects.get(pk=instance.id)
            youtube = YouTubeContent.objects.get(pk=c.youtubecontent)
            ret['video_id'] = youtube.video_id
            ret['is_youtube'] = True
        except Content.youtubecontent.RelatedObjectDoesNotExist:
            ret['is_youtube'] = False
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
        ret['content'] = ContentSerializer(instance.content).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        return ret


class CurveWithYouTubeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curve
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        value_type = ValueType.objects.get_or_none(
            title=self.initial_data["value_type"]["title"])
        content = YouTubeContent.objects.get_or_none(
            video_id=self.initial_data["youtube"]["video_id"])
        if not content:
            ser = YouTubeContentSerializer(data=self.initial_data["youtube"])
            if ser.is_valid():
                content = ser.save()
            else:
                return not bool(ser._errors)
        if not value_type:
            ser = ValueTypeSerializer(data=self.initial_data["value_type"])
            if ser.is_valid():
                value_type = ser.save()
            else:
                return not bool(ser._errors)
        self.initial_data["content"] = content.id
        self.initial_data["value_type"] = value_type.id
        return super().is_valid(raise_exception)


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
            values=validated_data['values'],
            description=validated_data['description']
        )
        instance.participants.set(validated_data['participants'])
        return instance
