import base64
import hashlib
import secrets
import time
from urllib.parse import urlencode
from uuid import UUID, uuid4

import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.core import signing
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST

from .models import CognitoIdentity, EmailUser, InvitingToken, Request, ValueType
from .serializers import UserSerializer


class SessionBackend(ModelBackend):
    """Only the successful Cognito callback can establish a session."""
    def authenticate(self, request, **credentials):
        return None


def app_url(path):
    return f"https://{settings.APP_BASE}{path}"


@require_GET
def start(request):
    verifier = secrets.token_urlsafe(48)
    state = secrets.token_urlsafe(32)
    request.session["oauth"] = {"state": state, "verifier": verifier, "started": time.time(),
                                "invitation": request.GET.get("invitation"),
                                "inviting": request.GET.get("inviting"),
                                "passport": request.GET.get("passport")}
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = urlencode({
        "response_type": "code", "client_id": settings.COGNITO_CLIENT_ID,
        "scope": "openid email", "redirect_uri": app_url("/api/cognito/callback/"),
        "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
    })
    return redirect(f"{settings.COGNITO_DOMAIN}/oauth2/authorize?{params}")


def resolve_user(subject, email):
    lookup = {"pool_id": settings.COGNITO_POOL_ID, "subject": subject}
    try:
        identity = CognitoIdentity.objects.select_related("user").get(**lookup)
    except CognitoIdentity.DoesNotExist:
        try:
            with transaction.atomic():
                user = EmailUser(username=uuid4().hex, email=email, is_verified=True)
                user.set_unusable_password()
                user.save()
                CognitoIdentity.objects.create(user=user, **lookup)
                user.groups.add(Group.objects.get(name="Guest"))
                return user
        except IntegrityError:
            identity = CognitoIdentity.objects.select_related("user").get(**lookup)
    user = identity.user
    if user.email != email or not user.is_verified:
        user.email = email
        user.is_verified = True
        user.save(update_fields=["email", "is_verified"])
    return user


@require_GET
def callback(request):
    oauth = request.session.pop("oauth", None)
    code = request.GET.get("code")
    state = request.GET.get("state", "")
    if (not oauth or not code or time.time() - oauth["started"] > 600
            or not secrets.compare_digest(oauth["state"].encode(), state.encode())):
        return HttpResponseBadRequest("認証の有効期限が切れました。ログインからやり直してください。")
    try:
        tokens = requests.post(f"{settings.COGNITO_DOMAIN}/oauth2/token", data={
            "grant_type": "authorization_code", "code": code, "code_verifier": oauth["verifier"],
            "redirect_uri": app_url("/api/cognito/callback/"), "client_id": settings.COGNITO_CLIENT_ID,
        }, timeout=8)
        tokens.raise_for_status()
        data = tokens.json()
        profile = requests.get(f"{settings.COGNITO_DOMAIN}/oauth2/userInfo", headers={
            "Authorization": f"Bearer {data['access_token']}"
        }, timeout=8)
        profile.raise_for_status()
        claims = profile.json()
        subject = UUID(claims["sub"])
        email = claims["email"]
        lifetime = int(data["expires_in"])
        if claims.get("email_verified") not in (True, "true") or not email or lifetime <= 0:
            raise ValueError()
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return HttpResponseBadRequest("Cognitoで本人確認ができませんでした。")
    user = resolve_user(subject, email)
    if not user.is_active:
        return JsonResponse({"message": "利用停止中のアカウントです。"}, status=403)
    try:
        if oauth.get("invitation"):
            invite = signing.loads(oauth["invitation"], salt="request-email", max_age=86400)
            if invite["email"].casefold() != email.casefold():
                raise ValueError()
            Request.objects.get(pk=invite["request"]).participants.add(user)
        if oauth.get("passport"):
            ids = signing.loads(oauth["passport"], salt="request-passport", max_age=7 * 86400)
            for item in Request.objects.filter(pk__in=ids):
                item.participants.add(user)
        if oauth.get("inviting"):
            invite = InvitingToken.objects.get(token=oauth["inviting"], expiration_date__gt=timezone.now(),
                                               user__groups__name="Researchers")
            user.inviting_users.add(invite.user)
            user.groups.add(Group.objects.get(name="Researchers"))
    except (signing.BadSignature, ValueError, Request.DoesNotExist, InvitingToken.DoesNotExist):
        return HttpResponseBadRequest("招待リンクが無効です。")
    login(request, user, backend="users.cognito.SessionBackend")
    request.session.set_expiry(lifetime)
    return redirect(app_url("/app/dashboard/"))


@require_POST
def sign_out(request):
    logout(request)
    params = urlencode({"client_id": settings.COGNITO_CLIENT_ID, "logout_uri": app_url("/")})
    return JsonResponse({"url": f"{settings.COGNITO_DOMAIN}/logout?{params}"})


class RequireCognitoSession:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in ("/api/cognito/login/", "/api/cognito/callback/") and not request.user.is_authenticated:
            return JsonResponse({"message": "ログインしてください。"}, status=401)
        return self.get_response(request)


@require_GET
def me(request):
    user = request.user
    value_type = ValueType.objects.filter(user=user, title="幸福度").order_by("pk").first()
    if not value_type:
        with transaction.atomic():
            EmailUser.objects.select_for_update().get(pk=user.pk)
            value_type, _ = ValueType.objects.get_or_create(user=user, title="幸福度", axis_type=1)
    return JsonResponse({**UserSerializer(user).data, "default_value_type": {"id": value_type.pk}})


@require_GET
def passport(request):
    ids = request.GET.get("ids", "").split(",")
    if len(ids) > 100 or not all(i.isascii() and i.isdigit() and len(i) <= 10 for i in ids):
        return HttpResponseBadRequest()
    owned = list(Request.objects.filter(owner=request.user, pk__in=ids).values_list("pk", flat=True))
    if set(owned) != {int(i) for i in ids}:
        return HttpResponseBadRequest()
    token = signing.dumps(owned, salt="request-passport")
    return JsonResponse({"url": app_url("/api/cognito/login/?") + urlencode({"passport": token})})
