import os
import time
import json
import asyncio

from django.utils.timezone import datetime, timedelta

from asgiref.sync import sync_to_async
import requests_async as requests
from importlib import import_module

from rest_framework.response import Response
from rest_framework import filters

from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .models import *

from .serializers import *

from backend.settings.common import AWS_STORAGE_BUCKET_NAME, S3_URL
from django.http import HttpResponse
from django.core.mail import send_mail

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django.http import JsonResponse

from lazysignup.decorators import allow_lazy_user

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import redirect

import boto3

from .serializers import *
from .models import *

User = get_user_model()


@method_decorator(allow_lazy_user, name='dispatch')
class Me(View):
    def get(self, request):
        return JsonResponse(UserSerializer(request.user).data, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    def get(self, request):
        token = request.GET.get("token")
        if token == None:
            return HttpResponse(status=403)
        if request.user.is_authenticated:
            logout(request)
        auth = JWTAuthentication()
        tokenAuth = JWTTokenUserAuthentication()
        token_user = tokenAuth.get_user(auth.get_validated_token(token))
        user = EmailUser.objects.get(pk=token_user.user_id)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("/")

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


@method_decorator(allow_lazy_user, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ValueTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all().order_by('created')
    search_fields = ['title']


@method_decorator(csrf_exempt, name='dispatch')
class ValueTypeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all()

    def get_queryset(self):
        return ValueType.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(allow_lazy_user, name='dispatch')
class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all().order_by('created')
    search_fields = ['title']


@method_decorator(csrf_exempt, name='dispatch')
class ContentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()

    def get_queryset(self):
        return Content.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class CurveHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all()

    def get_queryset(self):
        return Curve.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(allow_lazy_user, name='dispatch')
class CurveWithYouTubeContentViewSet(viewsets.ModelViewSet):
    serializer_class = CurveWithYouTubeSerializer
    queryset = Curve.objects.all().order_by('created')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(allow_lazy_user, name='dispatch')
class CurveViewSet(viewsets.ModelViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all().order_by('created')
    filter_backends = [filters.SearchFilter]
    search_fields = ['=room_name']


@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('date_joined')
    search_fields = ('username', 'email')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(allow_lazy_user, name='dispatch')
class YouTubeContentViewSet(viewsets.ModelViewSet):
    serializer_class = YouTubeContentSerializer
    queryset = YouTubeContent.objects.all().order_by('created')
    search_fields = ['=video_id']


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(allow_lazy_user, name='dispatch')
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
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(serializer.data, status=403)
    
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
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.data, status=403)


async def send_mail(request, title, description, participant):
    async with requests.Session() as session:
        response = await session.post(
            f"{os.environ.get('MAILGUN_API_BASE_URL')}/messages",
            auth=("api", os.environ.get("MAILGUN_API_KEY")),
            data={"from": f"{os.environ.get('MAILGUN_SENDER_NAME')} <{os.environ.get('MAILGUN_SMTP_LOGIN')}>",
                "to": [participant.email],
                "subject": title,
                "text": description
        })
        return (participant, request, response)
        


def split_list(array, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(array), n):
        yield array[idx:idx + n]


def send_mails(req):
    module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    participants = list(split_list(req.participants.all(), 5))
    for clique in participants:
        tasks = list()
        for participant in clique:
            access_token = RefreshToken.for_user(participant).access_token
            access_token.set_exp(lifetime=timedelta(days=1))
            title = f"【Request】 {req.title}"
            description = f"You got a request from {req.owner.username}({req.owner.email})\n"
            description += f"{'-' * 16}\n"
            description += f"{req.description}\n\n"
            description += f"You can click here to participate in\n"
            description += f"{module.APPLICATION_URL}api/login/?token={access_token}\n"
            description += f"{'-' * 16}\n\n"
            description += "Have a nice emonotating!\n"
            tasks.append(loop.create_task(send_mail(req, title, description, participant)))
        results, *_ = loop.run_until_complete(asyncio.wait(tasks))
        for result in results:
            participant, request, response = result.result()
            membership = participant.relationparticipant_set.get(request=request)
            membership.sended_mail = response.status_code == 200
            membership.message = response.json()["message"]
            membership.save()
        time.sleep(2.)
    loop.close()


@method_decorator(csrf_exempt, name='dispatch')
def send_request_mail(request, pk):
    request = Request.objects.get(pk=pk)
    send_mails(request)
    request.expiration_date = datetime.now() + timedelta(minutes=30)
    request.save()
    return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
def reset_email_addresses(request, pk):
    request = Request.objects.get(pk=pk)
    for participant in request.participants.all():
        participant.email = ""
        participant.save()
    data = RequestSerializer(request).data
    return JsonResponse(data=data)


@method_decorator(csrf_exempt, name='dispatch')
def get_email_list(request, pk):
    request = Request.objects.get(pk=pk)
    return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
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


@method_decorator(csrf_exempt, name='dispatch')
def get_download_curve_data(request, pk):
    s3 = boto3.client('s3')
    try:
        req = Request.objects.get(pk=pk)
        file_name = f"{req.room_name}.json"
        curves = Curve.objects.filter(room_name=req.room_name)
        curves_data = [CurveSerializer(curve).data for curve in curves]
        response = s3.put_object(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(curves_data),
            ACL="public-read")
        return JsonResponse(data={
            "url": f"{S3_URL}{file_name}",
            "file_name": file_name
        })
    except:
        return HttpResponse(status=404)
