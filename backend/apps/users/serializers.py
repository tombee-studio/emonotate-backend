import io
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *
from django.core.exceptions import ValidationError

from django.utils.translation import gettext as _

from datetime import datetime

from django.contrib.auth.models import Group


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

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
        ret["is_lazy_user"] = False
        ret["inviting_users"] = len(instance.inviting_users.all())
        ret["invited_users"] = len(instance.emailuser_set.all())
        ret["notifications"] = {
            "profile": profile_notifications
        }
        return ret


class PublicUserSerializer(serializers.ModelSerializer):
    """What other users may see about a user."""
    class Meta:
        model = User
        fields = ('id', 'username')


class ContactSerializer(serializers.ModelSerializer):
    """For the owner of a request or an invitation, who needs the address."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ValueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueType
        fields = '__all__'
        read_only_fields = ('user',)
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = PublicUserSerializer(instance.user).data
        return ret


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'
        read_only_fields = ('user',)
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = PublicUserSerializer(instance.user).data
        ret['is_youtube'] = hasattr(instance, 'youtubecontent')
        if ret['is_youtube']:
            ret['video_id'] = instance.youtubecontent.video_id
        if hasattr(instance, 'upload'):
            ret['data_type'] = instance.upload.mime_type
            ret['url'] = f"/api/sources/{instance.pk}/file/"
        return ret


class AnswerSerializer(serializers.ModelSerializer):
    """A row of the answers to a request; the points are read from the curve itself."""
    user = serializers.SerializerMethodField()

    class Meta:
        model = Curve
        fields = ('id', 'created', 'user', 'kind', 'version', 'locked')

    def get_user(self, curve):
        data = PublicUserSerializer(curve.user).data
        if curve.user_id in self.context['emails']:
            data['email'] = self.context['emails'][curve.user_id]
        return data


class ReadableContentMixin:
    """Accept only contents the user can read, with the error of an unknown one."""
    def validate_content(self, content):
        if self.instance and self.instance.content_id == content.pk:
            return content
        from .access import readable_contents
        if not readable_contents(self.context['request'].user).filter(pk=content.pk).exists():
            raise serializers.ValidationError(f'Invalid pk "{content.pk}" - object does not exist.')
        return content


class SectionSerializer(ReadableContentMixin, serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_webvtt(self, value):
        import webvtt
        try:
            webvtt.read_buffer(io.StringIO(value))
            return value
        except (webvtt.errors.MalformedCaptionError, webvtt.errors.MalformedFileError):
            raise ValidationError("区間情報が正しい形式に則っていません。WebVTT形式で入力してください。")


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        import webvtt
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
        read_only_fields = ('user',)
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = PublicUserSerializer(instance.user).data
        return ret


class EnqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquete
        fields = '__all__'


class GoogleFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleForm
        exclude = ('user',)


class CurveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curve
        fields = '__all__'
        read_only_fields = ('user',)
    
    def to_representation(self, instance):
        def generate_enquete_json(enquete, curve):
            data = EnqueteSerializer(enquete).data
            membership = enquete.enqueteanswer_set.get(curve=curve)
            data["answer"] = membership.answer
            return data
        ret = super().to_representation(instance)
        ret['user'] = PublicUserSerializer(instance.user).data
        ret['content'] = ContentSerializer(instance.content).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        ret['enquete'] = [generate_enquete_json(enquete, instance) for enquete in Enquete.objects.filter(pk__in=ret['enquete'])]
        return ret

    def validate(self, attrs):
        self.check_access(attrs)
        if 'values' in attrs:
            from .curve_values import clean_values
            content = attrs.get('content') or self.instance.content
            version = attrs.get('version') or self.instance.version
            is_text = hasattr(content, 'upload') and content.upload.mime_type == 'text/plain'
            try:
                attrs['values'] = clean_values(attrs['values'], version, is_text)
            except serializers.ValidationError as error:
                raise serializers.ValidationError({'values': error.detail})
        answers = self.initial_data.get("enquete", [])
        if not isinstance(answers, list):
            raise serializers.ValidationError({"enquete": "Expected a list."})
        if any(isinstance(answer, dict) for answer in answers):
            for answer in answers:
                if (not isinstance(answer, dict) or not isinstance(answer.get("id"), int)
                        or not isinstance(answer.get("answer"), str) or len(answer["answer"]) > 1000):
                    raise serializers.ValidationError({"enquete": "Invalid answer."})
            ids = {answer["id"] for answer in answers}
            if len(ids) != len(answers) or Enquete.objects.filter(pk__in=ids).count() != len(ids):
                raise serializers.ValidationError({"enquete": "Unknown or duplicate question."})
        return attrs

    def check_access(self, attrs):
        if 'request' not in self.context:
            return
        from rest_framework.exceptions import PermissionDenied
        from .access import joined_requests, readable_contents
        user = self.context['request'].user
        content = attrs.get('content')
        if (content and not (self.instance and self.instance.content_id == content.pk)
                and not readable_contents(user).filter(pk=content.pk).exists()):
            # The same error as for an unknown content.
            raise serializers.ValidationError({"content": f'Invalid pk "{content.pk}" - object does not exist.'})
        # A room name of a request marks the curve as an answer to it.
        room_name = attrs.get('room_name')
        if (room_name and Request.objects.filter(room_name=room_name).exists()
                and not joined_requests(user).filter(room_name=room_name).exists()):
            raise PermissionDenied("この依頼には回答できません。")

    def save(self, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            curve = super().save(**kwargs)
            for answer in self.initial_data.get("enquete", []):
                if isinstance(answer, dict):
                    EnqueteAnswer.objects.update_or_create(curve=curve, enquete_id=answer["id"],
                                                          defaults={"answer": answer["answer"]})
            return curve


class RequestSerializer(ReadableContentMixin, serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ('owner',)
    
    def to_representation(self, instance):
        def generate_user_json(user, request):
            data = ContactSerializer(user).data
            membership = user.relationparticipant_set.get(request=request)
            data["sended_mail"] = membership.sended_mail
            data["sended_mail_message"] = membership.message
            return data
        ret = super().to_representation(instance)
        ret['owner'] = PublicUserSerializer(instance.owner).data
        ret['content'] = ContentSerializer(Content.objects.get(pk=ret['content'])).data
        ret['value_type'] = ValueTypeSerializer(ValueType.objects.get(pk=ret['value_type'])).data
        viewer = getattr(self.context.get('request'), 'user', None)
        if viewer != instance.owner:
            ret['participants'] = []
            ret['is_many_participants'] = False
        elif len(ret['participants']) <= 10:
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


class GCPTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = GCPToken
        fields = '__all__'
