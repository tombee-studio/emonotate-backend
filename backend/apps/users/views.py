import boto3
from rest_framework.response import Response
from rest_framework import filters

from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .models import *

from .serializers import *

from backend.settings.common import AWS_STORAGE_BUCKET_NAME, S3_URL
from django.http import HttpResponse
import json

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django.http import JsonResponse

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    def post(self, request):
        params = json.loads(request.body)
        username = params['username']
        password = params['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'is_authenticated': True})
        return JsonResponse({'is_authenticated': False}, status=403)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'is_authenticated': False})


class ValueTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all().order_by('created')
    search_fields = 'id'


class ValueTypeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all()

    def get_queryset(self):
        return ValueType.objects.filter(user=self.request.user)


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all().order_by('created')


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


class CurveWithYouTubeContentViewSet(viewsets.ModelViewSet):
    serializer_class = CurveWithYouTubeSerializer
    queryset = Curve.objects.all().order_by('created')


class CurveViewSet(viewsets.ModelViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all().order_by('created')
    filter_backends = [filters.SearchFilter]
    search_fields = ['=room_name']

    def preprocess(self, request):
        if type(request.data["content"]) == dict:
            serializer = YouTubeContentSerializer(data=request.data["content"])
            if serializer.is_valid():
                serializer.save()
                request.data["content"] = serializer.data["id"]
            else:
                serializer = ContentSerializer(data=request.data["content"])
                if serializer.is_valid():
                    serializer.save()
                    request.data["content"] = serializer.data["id"]
                else:
                    exit(-1)
        if type(request.data["value_type"]) == dict:
            serializer = ValueTypeSerializer(data=request.data["value_type"])
            if serializer.is_valid():
                serializer.save()
                request.data["value_type"] = serializer.data["id"]
        return request

    def create(self, request, *args, **kwargs):
        request = self.preprocess(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request = self.preprocess(request)
        return super().update(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('date_joined')
    search_fields = ('username', 'email')


class YouTubeContentViewSet(viewsets.ModelViewSet):
    serializer_class = YouTubeContentSerializer
    queryset = YouTubeContent.objects.all().order_by('created')


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all().order_by('created')
    
    def get_queryset(self):
        role = self.request.GET.get('role')
        if role == 'owner':
            return self.queryset.filter(owner=self.request.user)
        elif role == 'participant':
            return self.request.user.request_set.all()
        else:
            return self.queryset
    
    def create(self, request, *args, **kwargs):
        def handle(email):
            try:
                return EmailUser.objects.get(email=email).id
            except:
                user = EmailUser.objects.create_unique_user(email=email)
                return user.id
        if not request.user.has_perm('users.add_request'):
            return Response("permission denied", status=403)
        request.data['participants'] = [ handle(email)
            for email in request.data['participants']]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
    
    def update(self, request, *args, **kwargs):
        def handle(email):
            try:
                return EmailUser.objects.get(email=email).id
            except:
                user = EmailUser.objects.create_unique_user(email=email)
                return user.id
        if not request.user.has_perm('users.change_request'):
            return Response("permission denied", status=403)
        request.data['participants'] = [ handle(email)
            for email in request.data['participants']]
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)


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

