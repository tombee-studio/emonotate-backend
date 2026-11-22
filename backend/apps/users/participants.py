from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.pagination import StandardPagination
from .models import EmailUser, RelationParticipant, Request, randomname

MAX_EMAILS = 1000


def find_or_create_users(emails):
    """The user of each address; an account that can sign in comes first."""
    users = {}
    for user in (EmailUser.objects.filter(email__in=emails)
                 .order_by("cognitoidentity__pk", "pk").select_related("cognitoidentity")):
        current = users.get(user.email)
        if not current or hasattr(user, "cognitoidentity") and not hasattr(current, "cognitoidentity"):
            users[user.email] = user
    missing = [email for email in emails if email not in users]
    created = EmailUser.objects.bulk_create([
        EmailUser(username=randomname(16), email=email, password=make_password(None)) for email in missing])
    groups = Group.objects.filter(name__in=("Guest", "General"))
    Membership = EmailUser.groups.through
    Membership.objects.bulk_create([Membership(emailuser_id=user.pk, group_id=group.pk)
                                    for user in created for group in groups])
    return [*users.values(), *created]


class ParticipantView(APIView):
    """The participants of a request, for its owner."""
    permission_classes = [IsAuthenticated]

    def get_request(self, pk, **kwargs):
        return get_object_or_404(Request.objects.select_for_update() if kwargs.get("lock") else Request,
                                 pk=pk, owner=self.request.user)

    def get(self, request, pk):
        rows = RelationParticipant.objects.filter(request=self.get_request(pk)).select_related("user")
        search = request.query_params.get("search", "").strip()
        if search:
            rows = rows.filter(Q(user__email__icontains=search) | Q(user__username__icontains=search))
        paginator = StandardPagination()
        page = paginator.paginate_queryset(rows.order_by("user__pk"), request)
        return paginator.get_paginated_response([{
            "id": row.user.pk, "username": row.user.public_name, "email": row.user.email,
            "sended_mail": row.sended_mail, "sended_mail_message": row.message,
        } for row in page])

    @transaction.atomic
    def post(self, request, pk):
        req = self.get_request(pk, lock=True)
        emails = request.data.get("emails") if isinstance(request.data, dict) else None
        if (not isinstance(emails, list) or not 0 < len(emails) <= MAX_EMAILS
                or not all(isinstance(email, str) for email in emails)):
            return Response({"detail": f"メールアドレスを1〜{MAX_EMAILS}件指定してください。"}, status=400)
        emails = list(dict.fromkeys(EmailUser.objects.normalize_email(email.strip()) for email in emails))
        invalid = []
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                invalid.append(email)
        if invalid:
            return Response({"detail": "メールアドレスを確認してください。", "invalid": invalid}, status=400)
        users = find_or_create_users(emails)
        joined = set(RelationParticipant.objects.filter(request=req, user__in=users).values_list("user", flat=True))
        added = [RelationParticipant(request=req, user=user) for user in users if user.pk not in joined]
        RelationParticipant.objects.bulk_create(added)
        return Response({"added": len(added), "total": RelationParticipant.objects.filter(request=req).count()},
                        status=201)

    @transaction.atomic
    def delete(self, request, pk):
        req = self.get_request(pk, lock=True)
        ids = request.data.get("ids") if isinstance(request.data, dict) else None
        if not isinstance(ids, list) or not all(type(i) is int for i in ids):
            return Response({"detail": "参加者を選択してください。"}, status=400)
        RelationParticipant.objects.filter(request=req, user__in=ids).delete()
        return Response({"total": RelationParticipant.objects.filter(request=req).count()})
