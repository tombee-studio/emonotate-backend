from uuid import UUID

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from users.models import CognitoIdentity, EmailUser


class Command(BaseCommand):
    help = "Bind a verified Cognito subject to a restored user before their first sign-in."

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("subject", type=UUID)

    def handle(self, user_id, subject, **options):
        try:
            with transaction.atomic():
                user = EmailUser.objects.select_for_update().get(pk=user_id)
                identity, _ = CognitoIdentity.objects.get_or_create(
                    pool_id=settings.COGNITO_POOL_ID, subject=subject, defaults={"user": user})
                if identity.user_id != user.pk:
                    raise CommandError("This Cognito subject already belongs to another user.")
        except EmailUser.DoesNotExist as exc:
            raise CommandError("User ID does not exist.") from exc
        except IntegrityError as exc:
            raise CommandError("This user already has a different Cognito identity.") from exc
        self.stdout.write(f"Linked user {user.pk}.")
