import io
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *
from django.core.exceptions import ValidationError

from django.utils.translation import gettext as _

from django.utils.timezone import datetime

from django.contrib.auth.models import Group

from lazysignup.utils import is_lazy_user

import webvtt

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        try:
            owner = EmailUser.objects.get(pk=attrs["id"])
        except:
            raise ValidationError(_('そのユーザは存在しません'), code='invalid username')
        try:
            if owner.email != attrs["email"]:
                user = EmailUser.objects.get(email=attrs["email"])
                raise ValidationError(_('そのメールアドレスはすでに使用されています'), code='invalid email')
        except EmailUser.DoesNotExist as ex:
            pass
        attrs["is_changed_email"] = owner.email != attrs["email"]
        return super().validate(attrs)

    def to_internal_value(self, data):
        data['groups'] = list([Group.objects.get(name=name).id for name in data['groups']])
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.email = validated_data['email']
        if validated_data["is_changed_email"]:
            instance.is_verified = False
        instance.save()
        return instance
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        profile_notifications = []
        if ret["is_verified"]:
            ret["groups"] = [group.name for group in instance.groups.all()]
        else:
            ret["groups"] = ["Guest"]
            profile_notifications.append("本人確認がされていないため、研究者向け機能を使用することができません。認証メールを送信し本人確認を行なってください。")
        ret["is_lazy_user"] = is_lazy_user(instance)
        ret["inviting_users"] = len(instance.inviting_users.all())
        ret["invited_users"] = len(instance.emailuser_set.all())
        ret["notifications"] = {
            "profile": profile_notifications
        }
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

    def validate_webvtt(self, value):
        try:
            webvtt.read_buffer(io.StringIO(value))
            return value
        except webvtt.errors.MalformedCaptionError as er:
            raise ValidationError("区間情報が正しい形式に則っていません。WebVTT形式で入力してください。")


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['content'] = ContentSerializer(instance.content).data
        try:
            out = webvtt.read_buffer(io.StringIO(instance.webvtt))
            ret['values'] = [{
                'start': point.start,
                'end': point.end,
                'text': point.text
            } for point in out]
            ret['is_incorrect_webvtt'] = False
        except webvtt.MalformedFileError:
            ret['values'] = []
            ret['is_incorrect_webvtt'] = True
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


class GoogleFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleForm
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
        if len(ret['participants']) <= 10:
            ret['participants'] = [generate_user_json(user, instance) for user in User.objects.filter(pk__in=ret['participants'])]
            ret['is_many_participants'] = False
        else:
            ret['participants'] = len(ret['participants'])
            ret['is_many_participants'] = True
        ret['enquetes'] = [EnqueteSerializer(enquete).data for enquete in Enquete.objects.filter(pk__in=ret['enquetes'])]
        ret['has_google_form'] = ret['google_form'] != None
        if ret['google_form'] != None:
            ret['google_form'] = GoogleFormSerializer(GoogleForm.objects.get(pk=ret['google_form'])).data
        if ret['section']:
            ret['is_included_section'] = True
            ret['section'] = SectionSerializer(Section.objects.get(pk=ret['section'])).data
        else:
            ret['is_included_section'] = False
        return ret
    
    def validate(self, attrs):
        return attrs
    
    def create(self, validated_data):
        instance = Request.objects.create(
            content=validated_data['content'],
            owner=validated_data['owner'],
            value_type=validated_data['value_type'],
            title=validated_data['title'],
            values=validated_data['values'],
            description=validated_data['description']
        )
        return instance
    
    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.owner = validated_data['owner']
        instance.value_type = validated_data['value_type']
        instance.title = validated_data['title']
        instance.values = validated_data['values']
        instance.description = validated_data['description']
        instance.is_required_free_hand = validated_data['is_required_free_hand']
        instance.save()
        return instance


class InvitingTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitingToken
        fields = '__all__'
