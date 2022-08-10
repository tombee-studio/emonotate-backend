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
from importlib import import_module

from .serializers import *
from .models import *

User = get_user_model()


class Me(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse(UserSerializer(request.user).data, status=200)
        else:
            return JsonResponse(data={
                "message": "not authenticated"
            }, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    def process_passport(self, queries, user):
        if queries.get("passport") == None:
            return
        passport = queries.get("passport")
        request_ids = [int(id_str) for id_str in passport.split(',')]
        for request in Request.objects.filter(pk__in=request_ids):
            request.participants.add(user)
            request.save()

    def get(self, request):
        token = request.GET.get("token")
        if request.user.is_authenticated:
            self.process_passport(request.GET, request.user)
            return redirect("/")

        if token == None:
            # *****
            # tokenがない場合、通常のログインプロセスへと移行
            # *****
            module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
            queries = [f'{query}={request.GET[query]}' for query in request.GET]
            return redirect(f"{module.APPLICATION_URL}app/login/{'' if not request.GET else '?' + '&'.join(queries)}")
        else:
            # *****
            # tokenがある場合、ユーザによるアクセスが保証されるため、JWT認証へと移行
            # *****
            if request.user.is_authenticated:
                logout(request)
            auth = JWTAuthentication()
            tokenAuth = JWTTokenUserAuthentication()
            token_user = tokenAuth.get_user(auth.get_validated_token(token))
            user = EmailUser.objects.get(pk=token_user.user_id)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            self.process_passport(request.GET, user)
            return redirect("/")

    def post(self, request):
        if not request.user.is_authenticated:
            if request.GET.get("guest"):
                # *******
                # ゲストユーザアカウントを作成してログイン
                # *******
                user = EmailUser.objects.create_unique_user()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            else:
                # *******
                # 既存のユーザアカウントを利用
                # *******
                params = json.loads(request.body)
                username = params['username']
                password = params['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        if request.user.is_authenticated:
            try:
                self.process_passport(request.GET, user)
            except err:
                pass
            return JsonResponse({
                'message': '正常にログインしました'
            })
        else:
            return JsonResponse({
                'message': 'ログインできませんでした',
            }, status_code=403)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'is_authenticated': False})


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
class CurveWithYouTubeContentViewSet(viewsets.ModelViewSet):
    serializer_class = CurveWithYouTubeSerializer
    queryset = Curve.objects.all().order_by('created')


@method_decorator(csrf_exempt, name='dispatch')
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
class YouTubeContentViewSet(viewsets.ModelViewSet):
    serializer_class = YouTubeContentSerializer
    queryset = YouTubeContent.objects.all().order_by('created')
    search_fields = ['=video_id']


@method_decorator(csrf_exempt, name='dispatch')
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


def send_mails(req, participants):
    if os.environ.get("STAGE") == "DEV":
        for clique in participants:
            for participant in clique:
                print(f"Sended {participant.email}")
                membership = participant.relationparticipant_set.get(request=req)
                membership.sended_mail = True
                membership.message = ""
                membership.save()
        return
    module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
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
        for r in results:
            participant, request, response = r.result()
            membership = participant.relationparticipant_set.get(request=request)
            membership.sended_mail = response.status_code == 200
            membership.message = response.json()["message"]
            membership.save()
        time.sleep(2.)
    loop.close()


@method_decorator(csrf_exempt, name='dispatch')
def send_request_mail(request, pk):
    req = Request.objects.get(pk=pk)
    emails = request.GET.get("targets")
    participants = []
    if emails == None:
        participants = req.participants.all()
    else:
        participants = req.participants.filter(pk__in=set([int(i) for i in emails.split(";")]))
    participants = split_list(list(participants), 5)
    send_mails(req, participants)
    req.expiration_date = datetime.now() + timedelta(minutes=30)
    req.save()
    data = RequestSerializer(req).data
    return JsonResponse(data=data, status=200)


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


@method_decorator(csrf_exempt, name='dispatch')
def download_curve_data(request):
    curve_ids = []
    if not request.user.is_authenticated:
        return JsonResponse({
            'message': 'user must be authenticated'
        }, status=403)
    if 'ids' in request.GET:
        curve_ids = list(map(lambda item: int(item), request.GET.get('ids').split(',')))
        if len(curve_ids) > 10:
            return JsonResponse({
                'message': 'too much the number(< 10) of curves to download'
            }, status=403)
    else:
        curve_ids = request.user.curve_set.all()
    s3 = boto3.client('s3')
    curves = Curve.objects.filter(pk__in=curve_ids)
    try:
        file_name = f"{request.user.username}.json"
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
