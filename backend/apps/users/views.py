import os
import re
import time
import json
import asyncio
import traceback

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

from rq import Queue
from worker import conn

from django.views.decorators.http import require_http_methods

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
    @staticmethod
    def is_invalid_emailuser(email):
        return re.match(r"emonotate\+.+@gmail.com", email)

    def process_queries(self, queries, user):
        self.process_passport(queries, user)
        self.process_inviting(queries, user)
    

    def process_inviting(self, queries, user):
        if queries.get("inviting") == None:
            return
        token = queries.get("inviting")
        token_obj = InvitingToken.objects.get(token=token)
        user.inviting_users.add(token_obj.user)
        user.save()


    def process_passport(self, queries, user):
        if queries.get("passport") == None:
            return
        passport = queries.get("passport")
        request_ids = [int(id_str) for id_str in passport.split(',')]
        for request in Request.objects.filter(pk__in=request_ids):
            request.participants.add(user)
            request.save()

    def get(self, request):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        token = request.GET.get("token")
        inviting = request.GET.get("inviting")
        if inviting != None:
            inviting_user = EmailUser.objects.create_unique_user()
            inviting_user.groups.add(Group.objects.get(name='Guest'))
            inviting_user.groups.add(Group.objects.get(name='Researchers'))
            self.process_queries(request.GET, inviting_user)
            login(request, inviting_user, backend='django.contrib.auth.backends.ModelBackend')
    
        if request.user.is_authenticated:
            self.process_queries(request.GET, request.user)
            return redirect(f"{module.APPLICATION_URL}")

        if token == None:
            # *****
            # tokenがない場合、通常のログインプロセスへと移行
            # *****
            queries = [f'{query}={request.GET[query]}' for query in request.GET]
            return redirect(f"{module.APPLICATION_URL}app/login/{'' if not request.GET else '?' + '&'.join(queries)}")

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
        self.process_queries(request.GET, user)
        return redirect("/")


    def post(self, request):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
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
                self.process_queries(request.GET, request.user)
            except Exception as ex:
                print(ex)
            if not LoginAPIView.is_invalid_emailuser(request.user.email):
                return JsonResponse(UserSerializer(request.user).data)
            else:
                return JsonResponse(data={
                    "url": f"{module.APPLICATION_URL}app/change_email/"
                }, status=302)
        else:
            return JsonResponse({
                'message': 'ログインできませんでした',
            }, status=403)


@method_decorator(csrf_exempt, name='dispatch')
class SignupAPIView(View):
    def process_passport(self, queries, user):
        if queries.get("passport") == None:
            return
        passport = queries.get("passport")
        request_ids = [int(id_str) for id_str in passport.split(',')]
        for request in Request.objects.filter(pk__in=request_ids):
            request.participants.add(user)
            request.save()

    def post(self, request):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        params = json.loads(request.body)
        username = params['username']
        email = params['email']
        password1 = params['password1']
        password2 = params['password2']
        try:
            if password1 != password2:
                raise "パスワードが一致しません"
            user = EmailUser.objects.create_user(username, email, password1)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            self.process_passport(request.GET, user)
            return JsonResponse({
                'is_authenticated': True
            }, status=201)
        except Exception as err:
            return JsonResponse({
                'message': err.__class__.__name__
            }, status=400) 


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
class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    queryset = Section.objects.all().order_by('created')
    search_fields = ['title', 'created']


@method_decorator(csrf_exempt, name='dispatch')
class GoogleFormViewSet(viewsets.ModelViewSet):
    serializer_class = GoogleFormSerializer
    queryset = GoogleForm.objects.all().order_by('created')
    search_fields = ['title', 'created']


@method_decorator(csrf_exempt, name='dispatch')
class EnqueteViewSet(viewsets.ModelViewSet):
    serializer_class = EnqueteSerializer
    queryset = Enquete.objects.all().order_by('created')
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
    search_fields = ['title']
    
    def get_queryset(self):
        role = self.request.GET.get('role')
        if role == 'owner':
            return self.queryset.filter(owner=self.request.user).order_by('created')
        elif role == 'participant':
            return self.request.user.request_set.all().order_by('created')
        elif role == 'relative':
            user = self.request.user
            invited_user_requests = self.queryset.filter(owner__in=user.emailuser_set.all())
            inviting_user_requests = self.queryset.filter(owner__in=user.inviting_users.all())
            return invited_user_requests.union(inviting_user_requests).order_by('created')
        else:
            return self.queryset.filter(owner=self.request.user).order_by('created')
    
    def create(self, request, *args, **kwargs):
        if not request.user.has_perm('users.add_request'):
            return Response("permission denied", status=403)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(serializer.data, status=403)
    
    def update(self, request, *args, **kwargs):
        if not request.user.has_perm('users.change_request'):
            return Response("permission denied", status=403)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.data, status=403)


class InvitingTokenView(View):
    def get(self, request, *args, **kwargs):
        try:
            token_obj = InvitingToken.objects.get(user=request.user)
            if token_obj.expiration_date > datetime.now():
                return JsonResponse({
                    "is_error": False,
                    "inviting_token": InvitingTokenSerializer(token_obj).data
                }, status=200)
            else:
                token_obj.delete()
        except InvitingToken.DoesNotExist:
            pass
        return JsonResponse({
            "is_error": True,
            "error": "GENERATE_INVITING_TOKEN_VIEW001",
            "message": "Inviting Tokenを作成したことがありません"
        },
        status=200)


    def post(self, request, *args, **kwargs):
        params = json.loads(request.body)
        expiration_date_str = params['expiration_date']
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%dT%H:%M")
        user = request.user
        try:
            token_obj = InvitingToken.objects.get(user=user)
            if datetime.now() < token_obj.expiration_date:
                return JsonResponse({
                    "is_error": True,
                    "error": "GENERATE_INVITING_TOKEN_VIEW002",
                    "message": "既に有効なInviting Tokenが存在しているためを作成できません",
                    "inviting_token": InvitingTokenSerializer(token_obj).data
                }, status=200)
            else:
                token_obj.delete()
        except InvitingToken.DoesNotExist:
            pass
        if expiration_date < datetime.now():
            return JsonResponse({
                "is_error": True,
                "error": "GENERATE_INVITING_TOKEN_VIEW003",
                "message": "現在以前に有効期限を設定することはできません"
            }, status=200)
        token_obj = InvitingToken(user=user, expiration_date=expiration_date)
        token_obj.save()
        return JsonResponse({
            "is_error": False,
            "inviting_token": InvitingTokenSerializer(token_obj).data
        }, status=201)


class ParticipantView(View):
    @staticmethod
    def json_dt_patch(o):
        import datetime
        from decimal import Decimal

        if isinstance(o, datetime.date) or isinstance(o, datetime.datetime):
            return o.strftime("%Y/%m/%d %H:%M:%S")
        elif isinstance(o, Decimal):
            return str(o)
        return o

    def get(self, request, pk=None, *args, **kwargs):
        req = Request.objects.get(pk=pk)
        if len(req.participants.all()) > 25:
            return JsonResponse({
                    "is_error": True,
                    "error": "PARTICIPANT_VIEW001",
                    "message": "参加者の人数が許容数を超えています",
                    "number": len(req.participants.all())
                },
                status=200)
        ser = UserSerializer(req.participants.all(), many=True)
        data = json.dumps(ser.data, default=ParticipantView.json_dt_patch)
        return JsonResponse({
            "is_error": False,
            "participants": json.loads(data)
        }, status=200)
    

    def post(self, request, pk, *args, **kwargs):
        req = Request.objects.get(pk=pk)
        params = json.loads(request.body)
        for email in params["emails"]:
            try:
                user = EmailUser.objects.get(email=email)
            except EmailUser.DoesNotExist:
                user = EmailUser.objects.create_unique_user(email)
                user.email = email
                user.save()
            req.participants.add(user)
            req.save()
        if len(req.participants.all()) > 25:
            return JsonResponse({
                    "is_error": True,
                    "error": "PARTICIPANT_VIEW001",
                    "message": "参加者の人数が許容数を超えています",
                    "number": len(req.participants.all())
                },
                status=200)
        ser = UserSerializer(req.participants.all(), many=True)
        data = json.dumps(ser.data, default=ParticipantView.json_dt_patch)
        return JsonResponse({
            "is_error": False,
            "participants": json.loads(data)
        }, status=200)
    
    def delete(self, request, pk, *args, **kwrags):
        req = Request.objects.get(pk=pk)
        params = json.loads(request.body)
        delete_participants = req.participants.filter(email__in=params)
        req.participants.remove(*delete_participants)
        req.save()
        if len(req.participants.all()) > 25:
            return JsonResponse({
                    "is_error": True,
                    "error": "PARTICIPANT_VIEW001",
                    "message": "参加者の人数が許容数を超えています",
                    "number": len(req.participants.all())
                },
                status=200)
        ser = UserSerializer(req.participants.all(), many=True)
        data = json.dumps(ser.data, default=ParticipantView.json_dt_patch)
        return JsonResponse({
            "is_error": False,
            "participants": json.loads(data)
        }, status=200)


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


def create_curve_data_in_s3(pk):
    s3 = boto3.client('s3')
    try:
        req = Request.objects.get(pk=pk)
        req.state_processing_to_download = 1
        req.save()
        file_name = f"{req.room_name}.json"
        curves = Curve.objects.filter(room_name=req.room_name)
        curves_data = CurveSerializer(curves, many=True).data
        response = s3.put_object(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(curves_data),
            ACL="public-read")
        req.state_processing_to_download = 2
        req.save()
    except:
        req.state_processing_to_download = -1
        req.save()


@method_decorator(csrf_exempt, name='dispatch')
def get_download_curve_data(request, pk):
    req = Request.objects.get(pk=pk)
    file_name = f"{req.room_name}.json"
    if req.state_processing_to_download == 0:
        # ダウンロード可能タイミング
        q = Queue(connection=conn)
        result = q.enqueue(create_curve_data_in_s3, pk)
        return JsonResponse(data={
            "state": "PROCESSING",
            "request": RequestSerializer(req).data
        })
    elif req.state_processing_to_download == 1:
        # 非同期が実行中の処理
        return JsonResponse(data={
            "state": "PROCESSING",
            "request": RequestSerializer(req).data
        })
    elif req.state_processing_to_download == 2:
        # 非同期が実行中の処理
        file_name = f"{req.room_name}.json"
        req.state_processing_to_download = 0
        req.save()
        return JsonResponse(data={
            "state": "SUCCESSED",
            "url": f"{S3_URL}{file_name}",
            "file_name": file_name,
            "request": RequestSerializer(req).data
        })
    elif req.state_processing_to_download == -1:
        req.state_processing_to_download = 0
        req.save()
        return JsonResponse(data={
            "state": "FAILED",
            "request": RequestSerializer(req).data
        })
    else:
        print(f"ERROR OCCUURED!!!! Invalid state_processing_to_download: {req.state_processing_to_download}")


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


@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["POST"])
def change_email(request):
    email = json.loads(request.body)["email"]
    if LoginAPIView.is_invalid_emailuser(email):
        return HttpResponse(json.dumps({
            "message": "無効なメールアドレスです",
            "error_code": "H10"
        }), status=403)
    try:
        existing_user = EmailUser.objects.get(email=email)
        return HttpResponse(json.dumps({
            "message": "そのメールアドレスは既に利用されています",
            "user": UserSerializer(existing_user).data,
            "error_code": "H11"
        }), status=403)
    except EmailUser.DoesNotExist:
        user = request.user
        user.email = email
        user.save()
        return JsonResponse(
            UserSerializer(EmailUser.objects.get(pk=user.id)).data, 
            status=202)


@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["POST"])
def merge_accounts(request):
    origin_name = json.loads(request.body)["from"]
    to_name = json.loads(request.body)["to"]
    password = json.loads(request.body)["password"]
    user = authenticate(request, username=to_name, password=password)
    if user is not None:
        origin_user = EmailUser.objects.get(username=origin_name)
        to_user = EmailUser.objects.get(username=to_name)
        login(request, to_user, backend='django.contrib.auth.backends.ModelBackend')
        tasks = []
        for item in origin_user.curve_set.all():
            item.user = to_user
            tasks.append(item)
        Curve.objects.bulk_update(tasks, ["user"])
        origin_user.delete()
        return HttpResponse(json.dumps({
            "user": UserSerializer(to_user).data
        }), status=202)
    else:
        return HttpResponse(json.dumps({
            "message": f"{EmailUser.objects.get(username=to_name).username}のパスワードを入力してください",
            "error_code": "H09"
        }), status=403)