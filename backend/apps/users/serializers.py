from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *

from django.utils.timezone import datetime

from django.contrib.auth.models import Group

from lazysignup.utils import is_lazy_user

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    def to_internal_value(self, data):
        data['groups'] = list([Group.objects.get(name=name).id for name in data['groups']])
        return data
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["groups"] = [group.name for group in instance.groups.all()]
        ret["is_lazy_user"] = is_lazy_user(instance)
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


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['content'] = ContentSerializer(instance.content).data
        return ret


class YouTubeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeContent
        fields = '__all__'
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(User.objects.get(pk=ret['user'])).data
        return ret


class EnqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquete
        fields = '__all__'


class CurveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curve
        fields = '__all__'
    
    def to_representation(self, instance):
        def generate_enquete_json(enquete, curve):
            data = EnqueteSerializer(enquete).data
            membership = enquete.enqueteanswer_set.get(curve=curve)
            data["answer"] = membership.answer
            return data
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(User.objects.get(pk=ret['user'])).data
        ret['content'] = ContentSerializer(instance.content).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        ret['enquete'] = [generate_enquete_json(enquete, instance) for enquete in Enquete.objects.filter(pk__in=ret['enquete'])]
        return ret

    def validate(self, attrs):
        attrs['enquete'] = list(map(lambda item: item["id"], self.initial_data['enquete']))
        return attrs
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        enquetes = Enquete.objects.filter(pk__in=list(map(lambda item: item["id"], self.initial_data['enquete'])))
        for enquete in enquetes.iterator():
            _item = enquete.enqueteanswer_set.get(curve=instance)
            answer_item = list(filter(lambda item: item["id"] == enquete.id, self.initial_data['enquete']))[0]
            _item.answer = answer_item["answer"]
            _item.save()
        return instance


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


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
    
    def to_representation(self, instance):
        def generate_user_json(user, request):
            data = UserSerializer(user).data
            membership = user.relationparticipant_set.get(request=request)
            data["sended_mail"] = membership.sended_mail
            data["sended_mail_message"] = membership.message
            return data
        ret = super().to_representation(instance)
        ret['owner'] = UserSerializer(User.objects.get(pk=ret['owner'])).data
        ret['content'] = ContentSerializer(Content.objects.get(pk=ret['content'])).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        ret['participants'] = [generate_user_json(user, instance) for user in User.objects.filter(pk__in=ret['participants'])]
        ret['enquetes'] = [EnqueteSerializer(enquete).data for enquete in Enquete.objects.filter(pk__in=ret['enquetes'])]
        ret['section'] = SectionSerializer(Section.objects.get(pk=ret['section'])).data
        return ret
    
    def validate(self, attrs):
        attrs['participants'] = self.initial_data['participants']
        attrs['enquetes'] = self.initial_data['enquetes']
        return attrs
    
    def create(self, validated_data):
        instance = Request.objects.create(
            content=validated_data['content'],
            owner=validated_data['owner'],
            value_type=validated_data['value_type'],
            title=validated_data['title'],
            values=validated_data['values'],
            description=validated_data['description'],
            section=validated_data['section']
        )
        instance.participants.set(validated_data['participants'])
        instance.enquetes.set(validated_data['enquetes'])
        return instance
