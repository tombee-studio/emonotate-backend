import boto3

from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .models import ValueType, Curve, Content

from .serializers import *

from backend.settings.common import AWS_STORAGE_BUCKET_NAME, S3_URL
from django.http import HttpResponse
import json

User = get_user_model()


class ValueTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all()
    search_fields = 'id'


class ValueTypeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all()

    def get_queryset(self):
        return ValueType.objects.filter(user=self.request.user)


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()


class ContentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()

    def get_queryset(self):
        return Content.objects.filter(user=self.request.user)


class CurveHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all()

    def get_queryset(self):
        return Curve.objects.filter(user=self.request.user)


class CurveViewSet(viewsets.ModelViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all()
    search_fields = ('id', 'user')


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    search_fields = ('username', 'email')


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    
    def get_queryset(self):
        role = self.request.GET.get('role')
        if role == 'owner':
            return self.queryset.filter(owner=self.request.user)
        elif role == 'participant':
            return self.request.user.request_set.all()
        else:
            return self.queryset


def sign_s3(request):
    file_name = request.GET['file_name']
    file_type = request.GET['file_type']

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket=AWS_STORAGE_BUCKET_NAME,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type}
        ],
        ExpiresIn=3600
    )

    return HttpResponse(json.dumps({
        'data': presigned_post,
        'url': '%s%s' % (S3_URL, file_name)
    }))

