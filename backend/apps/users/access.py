"""Who can read or change what. The table is in docs/access.md."""
from django.db.models import F, Q
from rest_framework.exceptions import PermissionDenied

from .models import Content, Curve, EnqueteAnswer, Request


def joined_requests(user):
    """Requests the user can answer: the user's own and those sent to the user."""
    sent = user.request_set.values("pk")
    return Request.objects.filter(Q(owner=user) | Q(pk__in=sent))


def relative_requests(user):
    """Requests of the users who invited this user or were invited by this user."""
    return Request.objects.filter(Q(owner__in=user.emailuser_set.values("pk")) |
                                  Q(owner__in=user.inviting_users.values("pk")))


def readable_requests(user):
    return joined_requests(user) | relative_requests(user)


def readable_contents(user):
    """Public contents, the user's own, and uploads their owner requested the user to watch."""
    requested = Request.objects.filter(pk__in=user.request_set.values("pk"), owner=F("content__user"))
    return Content.objects.filter(Q(upload__isnull=True) | Q(user=user) |
                                  Q(pk__in=requested.values("content")))


def readable_curves(user):
    """The user's own curves and the answers to the requests of the user."""
    owned = Request.objects.filter(owner=user)
    return Curve.objects.filter(Q(user=user) | Q(room_name__in=owned.values("room_name")))


def check_value_type_unused(value_type, user):
    if (Curve.objects.filter(value_type=value_type).exclude(user=user).exists() or
            Request.objects.filter(value_type=value_type).exclude(owner=user).exists()):
        raise PermissionDenied("ほかの利用者が使用しているため削除できません。")


def check_axis_type_unused(value_type):
    """The axis type decides the range of the saved curves."""
    if (Curve.objects.filter(value_type=value_type).exists() or
            Request.objects.filter(value_type=value_type).exists()):
        raise PermissionDenied("使用中の評価軸の種類は変更できません。")


def check_content_unused(content, user):
    if (Curve.objects.filter(content=content).exists() or
            Request.objects.filter(content=content).exclude(owner=user).exists()):
        raise PermissionDenied("使用されているため削除できません。")


def check_enquete_unused(enquete, user):
    """Questions have no owner, so one that others use must stay as it is."""
    if (EnqueteAnswer.objects.filter(enquete=enquete).exists() or
            Request.objects.filter(enquetes=enquete).exclude(owner=user).exists()):
        raise PermissionDenied("使用されている設問は変更できません。")
