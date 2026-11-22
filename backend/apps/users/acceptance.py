"""Whether a request still accepts an answer of a person."""
from datetime import datetime

from rest_framework.exceptions import PermissionDenied

from .models import Curve, EmailUser, Request


def closed_reason(request, user, curve=None):
    """Why the user cannot save an answer now; None when it is accepted.

    curve is the saved curve being changed, which does not count as a new answer.
    """
    now = datetime.now()
    if request.starts_at and now < request.starts_at:
        return f"受付は {request.starts_at:%Y/%m/%d %H:%M} からです。"
    if request.ends_at and now >= request.ends_at:
        return f"受付は {request.ends_at:%Y/%m/%d %H:%M} に終了しました。"
    if request.max_submissions:
        answers = Curve.objects.filter(user=user, room_name=request.room_name)
        if curve:
            answers = answers.exclude(pk=curve.pk)
        if answers.count() >= request.max_submissions:
            return f"提出できる回数({request.max_submissions}回)に達しています。"
    return None


def check_accepted(room_name, user, curve=None):
    """Call inside a transaction that also saves the curve."""
    if not room_name:
        return
    request = Request.objects.filter(room_name=room_name).first()
    if not request:
        return
    # One person's answers are saved one after another, so that the count holds.
    EmailUser.objects.select_for_update().get(pk=user.pk)
    reason = closed_reason(request, user, curve)
    if reason:
        raise PermissionDenied(reason)
