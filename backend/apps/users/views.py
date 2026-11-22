import os
import re
import time
import json
import asyncio
import traceback

try:
    import firebase_admin
    from firebase_admin import credentials
    _has_firebase = True
except ImportError:
    _has_firebase = False

from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
import requests
import requests as requests_sync
from importlib import import_module

from rest_framework.response import Response
from rest_framework import filters

from rest_framework import viewsets
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from .models import *

from .serializers import *

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from .sources import storage
from . import access
from .acceptance import check_accepted
from .participants import ParticipantView
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django.http import JsonResponse


from django.shortcuts import redirect

from importlib import import_module


from django.views.decorators.http import require_http_methods

from .serializers import *
from .models import *

User = get_user_model()


def send_mail(user, title, description):
    module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
    return requests.post(
        f"{os.environ.get('MAILGUN_API_BASE_URL')}/messages",
        auth=("api", os.environ.get("MAILGUN_API_KEY")),
        data={"from": f"{os.environ.get('MAILGUN_SENDER_NAME')} <{os.environ.get('MAILGUN_SMTP_LOGIN')}>",
            "to": [user.email],
            "subject": title,
            "text": description
    })


class Me(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse(UserSerializer(request.user).data, status=200)
        else:
            return JsonResponse(data={
                "message": "not authenticated"
            }, status=401)

class MailGenerator:
    @staticmethod
    def create_verify_mail(user):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        from rest_framework_simplejwt.tokens import RefreshToken
        access_token = RefreshToken.for_user(user).access_token
        access_token.set_exp(lifetime=timedelta(minutes=30))
        title = f"【Important】 Sending Verification URL"
        description = ""
        description += f"This is Emonotate Operating Staff.\n"
        description += f"We send a url to verify below:\n"
        description += f"{module.APPLICATION_URL}api/verify/?token={access_token}\n"
        description += f"{'-' * 16}\n\n"
        description += "Have a nice emonotating!\n"
        return (title, description)

    @staticmethod
    def create_password_reset_mail(user):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        from rest_framework_simplejwt.tokens import RefreshToken
        access_token = RefreshToken.for_user(user).access_token
        access_token.set_exp(lifetime=timedelta(minutes=30))
        title = f"【Important】 Sending Password Reset URL"
        description = ""
        description += f"This is Emonotate Operating Staff.\n"
        description += f"We send a url to reset your password below:\n"
        description += f"{module.APPLICATION_URL}api/login/?token={access_token}\n"
        description += f"{'-' * 16}\n\n"
        description += "Have a nice emonotating!\n"
        return (title, description)


class UserAuthenticationModule:
    @staticmethod
    def process_queries(queries, user):
        instance = UserAuthenticationModule()
        instance.process_passport(queries, user)
        instance.process_inviting(queries, user)

    def process_inviting(self, queries, user):
        if queries.get("inviting") == None:
            return
        token = queries.get("inviting")
        token_obj = InvitingToken.objects.get(token=token)
        user.inviting_users.add(token_obj.user)
        user.groups.add(Group.objects.get(name='Guest'))
        user.groups.add(Group.objects.get(name='Researchers'))
        user.save()


    def process_passport(self, queries, user):
        if queries.get("passport") == None:
            return
        passport = queries.get("passport")
        request_ids = [int(id_str) for id_str in passport.split(',')]
        for request in Request.objects.filter(pk__in=request_ids):
            request.participants.add(user)
            request.save()


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    @staticmethod
    def is_invalid_emailuser(email):
        return re.match(r"emonotate\+.+@gmail.com", email)


    def get(self, request):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        token = request.GET.get("token")
        inviting = request.GET.get("inviting")
        if request.user.is_authenticated:
            try:
                UserAuthenticationModule.process_queries(request.GET, request.user)
                return redirect(f"{module.APPLICATION_URL}")
            except:
                return redirect(f"{module.APPLICATION_URL}?error=無効なURLです")
        else:
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
            from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
            auth = JWTAuthentication()
            tokenAuth = JWTTokenUserAuthentication()
            token_user = tokenAuth.get_user(auth.get_validated_token(token))
            user = EmailUser.objects.get(pk=token_user.user_id)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            UserAuthenticationModule.process_queries(request.GET, request.user)
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
                UserAuthenticationModule.process_queries(request.GET, request.user)
            except Exception as ex:
                print(ex)
            if not LoginAPIView.is_invalid_emailuser(request.user.email):
                return JsonResponse(UserSerializer(request.user).data)
            else:
                queries = [f'{query}={request.GET[query]}' for query in request.GET]
                return JsonResponse({
                    'url': f"{module.APPLICATION_URL}api/login/{'' if not request.GET else '?' + '&'.join(queries)}"
                }, status=302)
        else:
            return JsonResponse({
                "is_error": True,
                'message': 'ログインできませんでした',
            }, status=403)


@method_decorator(csrf_exempt, name='dispatch')
class SignupAPIView(View):
    def post(self, request):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        params = json.loads(request.body)
        username = params['username']
        email = params['email']
        password1 = params['password1']
        password2 = params['password2']
        
        if password1 != password2:
            return HttpResponse("パスワードが一致しません", status=404)

        try:
            user = EmailUser.objects.get(username=username)
            return HttpResponse(f"ユーザ名はすでに使用されています", status=404)
        except:
            pass

        try:
            user = EmailUser.objects.get(email=email)
            return HttpResponse(f"そのメールアドレスはすでに使用されています", status=404)
        except:
            pass

        user = EmailUser.objects.create_user(username, email, password1)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        queries = [f'{query}={request.GET[query]}' for query in request.GET]
        try:
            from rq import Queue
            from worker import conn
            q = Queue(connection=conn)
            (title, description) = MailGenerator.create_verify_mail(user)
            q.enqueue(send_mail, user, title, description)
        except Exception:
            pass
        return JsonResponse({
            "is_error": False,
            'url': f"{module.APPLICATION_URL}api/login/{'' if not request.GET else '?' + '&'.join(queries)}"
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserVerifyView(View):
    def get(self, request):
        module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
        if "token" not in request.GET:
            message = "無効な認証用URLです"
            return redirect(f"{module.APPLICATION_URL}app/login/?error={message}")
        try:
            token = request.GET.get("token")

            from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
            auth = JWTAuthentication()
            tokenAuth = JWTTokenUserAuthentication()
            token_user = tokenAuth.get_user(auth.get_validated_token(token))
            user = EmailUser.objects.get(pk=token_user.user_id)
            user.is_verified = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(f"{module.APPLICATION_URL}app/")
        except:
            message = "無効な認証用URLです"
            return redirect(f"{module.APPLICATION_URL}app/login/?error={message}")

    def post(self, request):
        user = request.user
        if not request.user.is_authenticated:
            return HttpResponse("認証されていないユーザです", status=403)
        try:
            from rq import Queue
            from worker import conn
            q = Queue(connection=conn)
            (title, description) = MailGenerator.create_verify_mail(user)
            q.enqueue(send_mail, user, title, description)
        except Exception:
            pass
        return HttpResponse("認証用メールを送信しました", status=200)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'is_authenticated': False})


class OwnerWriteMixin:
    """Everyone can read what get_readable() allows; only the owner can change it."""
    def get_readable(self):
        return super().get_queryset()

    def get_queryset(self):
        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            return super().get_queryset().filter(user=self.request.user)
        return self.get_readable()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class ValueTypeViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all().order_by('created')
    search_fields = ['title']

    def perform_destroy(self, instance):
        access.check_value_type_unused(instance, self.request.user)
        instance.delete()


@method_decorator(csrf_exempt, name='dispatch')
class ValueTypeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all()

    def get_queryset(self):
        return ValueType.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class ContentViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all().order_by('created').reverse()
    search_fields = ['title']

    def get_readable(self):
        return access.readable_contents(self.request.user).order_by('-created')

    def perform_destroy(self, instance):
        access.check_content_unused(instance, self.request.user)
        instance.delete()


@method_decorator(csrf_exempt, name='dispatch')
class SectionViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    queryset = Section.objects.all().order_by('created').reverse()
    search_fields = ['title', 'created']

    def get_readable(self):
        from django.db.models import Q
        requests = access.joined_requests(self.request.user)
        return self.queryset.filter(Q(user=self.request.user) | Q(pk__in=requests.values('section')))


@method_decorator(csrf_exempt, name='dispatch')
class GoogleFormViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = GoogleFormSerializer
    queryset = GoogleForm.objects.all().order_by('created').reverse()
    search_fields = ['title', 'created']

    def get_readable(self):
        from django.db.models import Q
        requests = access.joined_requests(self.request.user)
        return self.queryset.filter(Q(user=self.request.user) | Q(pk__in=requests.values('google_form')))


@method_decorator(csrf_exempt, name='dispatch')
class EnqueteViewSet(viewsets.ModelViewSet):
    serializer_class = EnqueteSerializer
    queryset = Enquete.objects.all().order_by('created').reverse()
    search_fields = ['title']

    def perform_update(self, serializer):
        access.check_enquete_unused(serializer.instance, self.request.user)
        serializer.save()

    def perform_destroy(self, instance):
        access.check_enquete_unused(instance, self.request.user)
        instance.delete()


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
        return Curve.objects.filter(user=self.request.user).order_by("-created", "-pk")


@method_decorator(csrf_exempt, name='dispatch')
class OwnCurveViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if self.action == 'retrieve':
            return access.readable_curves(self.request.user)
        return super().get_queryset().filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        check_accepted(serializer.validated_data.get('room_name'), self.request.user)
        serializer.save(user=self.request.user)

    def check_unlocked(self, curve):
        if curve.locked:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("この曲線はロックされています。")

    @transaction.atomic
    def perform_update(self, serializer):
        curve = serializer.instance
        self.check_unlocked(curve)
        check_accepted(serializer.validated_data.get('room_name', curve.room_name), self.request.user, curve)
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        self.check_unlocked(instance)
        instance.delete()


@method_decorator(csrf_exempt, name='dispatch')
class CurveViewSet(OwnCurveViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all().order_by('created').reverse()
    filter_backends = [filters.SearchFilter]
    search_fields = ['=room_name']


@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('date_joined').reverse()
    search_fields = ('username', 'email')

    def get_queryset(self):
        if getattr(settings, 'COGNITO_POOL_ID', None):
            if self.request.method not in ('GET', 'HEAD', 'OPTIONS'):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("アカウントはCognitoで管理されています。")
        return super().get_queryset().filter(pk=self.request.user.pk)


@method_decorator(csrf_exempt, name='dispatch')
class YouTubeContentViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = YouTubeContentSerializer
    queryset = YouTubeContent.objects.all().order_by('created').reverse()
    search_fields = ['=video_id']

    def perform_destroy(self, instance):
        access.check_content_unused(instance, self.request.user)
        instance.delete()


@method_decorator(csrf_exempt, name='dispatch')
class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all().order_by('created')
    search_fields = ['title']
    
    def get_queryset(self):
        if self.request.method not in ('GET', 'HEAD', 'OPTIONS'):
            return self.queryset.filter(owner=self.request.user)
        role = self.request.GET.get('role')
        if role == 'owner':
            return self.queryset.filter(owner=self.request.user).order_by('created').reverse()
        elif role == 'participant':
            return self.request.user.request_set.all().order_by('created').reverse()
        elif role == 'relative':
            return access.relative_requests(self.request.user).order_by('created').reverse()
        else:
            return access.readable_requests(self.request.user).order_by('created').reverse()

    @action(detail=True, methods=['get'])
    def curves(self, request, pk=None):
        req = get_object_or_404(Request, pk=pk, owner=request.user)
        curves = Curve.objects.filter(room_name=req.room_name).select_related('user').order_by('-created', '-pk')
        page = self.paginate_queryset(curves)
        # The owner knows the addresses of the participants only.
        emails = dict(req.participants.filter(pk__in=[curve.user_id for curve in page]).values_list('pk', 'email'))
        return self.get_paginated_response(AnswerSerializer(page, many=True, context={'emails': emails}).data)

    def create(self, request, *args, **kwargs):
        if not request.user.has_perm('users.add_request'):
            return Response("permission denied", status=403)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(serializer.data, status=403)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "mode" in request.data:
            if request.data["mode"] == "duplicate":
                enquetes = list(instance.enquetes.all())
                instance.id = None
                instance.owner = request.user
                instance.room_name = ""
                with transaction.atomic():
                    instance.save()
                    instance.enquetes.set(enquetes)
                ser = self.get_serializer(instance)
                return Response(ser.data, status=201)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.data, status=403)


class InvitingTokenView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Researchers").exists():
            return HttpResponse(status=403)
        return super().dispatch(request, *args, **kwargs)

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


class RelativeUsersView(View):
    @staticmethod
    def json_dt_patch(o):
        import datetime
        from decimal import Decimal

        if isinstance(o, datetime.date) or isinstance(o, datetime.datetime):
            return o.strftime("%Y/%m/%d %H:%M:%S")
        elif isinstance(o, Decimal):
            return str(o)
        return o

    def get(self, request, *args, **kwargs):
        user = request.user
        invited_users = user.emailuser_set.all()
        inviting_users = user.inviting_users.all()
        ser = ContactSerializer(invited_users.union(inviting_users).order_by("id"), many=True)
        data = json.dumps(ser.data, default=RelativeUsersView.json_dt_patch)
        return JsonResponse({
            "is_error": False,
            "users": json.loads(data)
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(View):
    def post(self, request):
        params = json.loads(request.body)
        email = params["email"]
        try:
            user = EmailUser.objects.get(email=email)
            try:
                from rq import Queue
                from worker import conn
                q = Queue(connection=conn)
                (title, description) = MailGenerator.create_password_reset_mail(user)
                q.enqueue(send_mail, user, title, description)
            except Exception:
                pass
            return HttpResponse("パスワードリセットのためのメールを送信しました", status=200)
        except:
            return HttpResponse("無効なメールアドレスです", status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(View):
    def put(self, request, pk, *args, **kwargs):
        params = json.loads(request.body)
        password1 = params["password"]
        password2 = params["password2"]
        if password1 != password2:
            return HttpResponse("確認用のパスワードが一致していません", status=400)
        user = EmailUser.objects.get(pk=pk)
        user.set_password(password1)
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponse("パスワードを変更しました", status=200)


class SetSectionView(View):
    def put(self, request, pk, *args, **kwargs):
        req = get_object_or_404(Request, pk=pk, owner=request.user)
        req.section = get_object_or_404(Section, pk=json.loads(request.body)["section"], user=request.user)
        req.save()
        return HttpResponse("区間情報を変更しました", status=200)


class SetGoogleFormView(View):
    def put(self, request, pk, *args, **kwargs):
        req = get_object_or_404(Request, pk=pk, owner=request.user)
        req.google_form = get_object_or_404(GoogleForm, pk=json.loads(request.body)["google_form"],
                                            user=request.user)
        req.save()
        return HttpResponse("Google フォームを変更しました", status=200)


@method_decorator(csrf_exempt, name='dispatch')
class GCPAccessTokenView(View):
    def validate_access_token(self, gcptoken):
        url = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
        res = requests_sync.get(url, {'access_token': gcptoken.access_token})
        if res.json().get('error_description', None) is None:
            return True
        return False
    
    def post(self, request, *args, **kwargs):
        gcptoken = GCPToken.objects.get(pk=1)
        response_data = GCPTokenSerializer(gcptoken).data
        credential = credentials.Certificate('./google-credentials.json')
        accessTokenInfo = credential.get_access_token()
        response_data["access_token"] = accessTokenInfo.access_token
        return JsonResponse(response_data, status=200)


def split_list(array, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(array), n):
        yield array[idx:idx + n]


def send_request_mails(req, participants):
    if os.environ.get("STAGE") == "DEV":
        for clique in participants:
            for participant in clique:
                membership = participant.relationparticipant_set.get(request=req)
                membership.sended_mail = True
                membership.message = ""
                membership.save()
        return
    from django.core import signing
    from urllib.parse import urlencode
    for clique in participants:
        for participant in clique:
            token = signing.dumps({"request": req.pk, "email": participant.email}, salt="request-email")
            link = settings.APPLICATION_URL + "api/cognito/login/?" + urlencode({"invitation": token})
            description = f"{req.owner.username}さんからの依頼です。\n{req.description}\n{link}"
            result = send_mail(participant, f"【Request】 {req.title}", description)
            membership = participant.relationparticipant_set.get(request=req)
            membership.sended_mail = result.ok
            membership.message = str(result.status_code)
            membership.save()


@require_http_methods(["POST"])
def send_request_mail(request, pk):
    req = get_object_or_404(Request, pk=pk, owner=request.user)
    emails = request.GET.get("targets")
    participants = []
    if emails == None:
        participants = req.participants.all()
    else:
        participants = req.participants.filter(pk__in=set([int(i) for i in emails.split(";")]))
    participants = split_list(list(participants), 5)
    send_request_mails(req, participants)
    req.expiration_date = datetime.now() + timedelta(minutes=30)
    req.save()
    data = RequestSerializer(req, context={"request": request}).data
    return JsonResponse(data=data, status=200)


def s3_download_url(key):
    return storage().generate_presigned_url("get_object", Params={
        "Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key,
    }, ExpiresIn=300)


@require_http_methods(["GET"])
def get_download_curve_data(request, pk):
    req = get_object_or_404(Request, pk=pk, owner=request.user)
    file_name = f"{req.room_name}.json"
    key = f"exports/{request.user.pk}/{file_name}"
    curves = CurveSerializer(Curve.objects.filter(room_name=req.room_name), many=True).data
    # The owner knows the participants, so their addresses stay in the export.
    emails = dict(req.participants.values_list("pk", "email"))
    for curve in curves:
        if curve["user"]["id"] in emails:
            curve["user"]["email"] = emails[curve["user"]["id"]]
    storage().put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key,
                         Body=json.dumps(curves), ContentType="application/json")
    return JsonResponse({"state": "SUCCESSED", "url": s3_download_url(key), "file_name": file_name,
                         "request": RequestSerializer(req, context={"request": request}).data})


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
    s3 = storage()
    curves = request.user.curve_set.filter(pk__in=curve_ids)
    try:
        file_name = f"{request.user.username}.json"
        key = f"exports/{request.user.pk}/curves.json"
        curves_data = [CurveSerializer(curve).data for curve in curves]
        response = s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            Body=json.dumps(curves_data), ContentType="application/json")
        return JsonResponse(data={
            "url": s3_download_url(key),
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