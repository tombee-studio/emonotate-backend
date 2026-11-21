from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from users.models import Content, UploadedSource
from users.sources import FORMATS, storage


class Command(BaseCommand):
    help = "Associate an existing private S3 object with a restored content record."

    def add_arguments(self, parser):
        parser.add_argument("content_id", type=int)
        parser.add_argument("key")

    def handle(self, content_id, key, **options):
        obj = storage().head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        mime = obj["ContentType"].split(";")[0]
        if mime not in FORMATS:
            raise CommandError("Unsupported S3 object content type.")
        try:
            with transaction.atomic():
                content = Content.objects.select_for_update().get(pk=content_id)
                if hasattr(content, "youtubecontent"):
                    raise CommandError("This content is a YouTube video.")
                source, _ = UploadedSource.objects.get_or_create(content=content, defaults={"key": key, "mime_type": mime})
                if source.key != key:
                    raise CommandError("This content already has a different S3 object.")
        except (Content.DoesNotExist, IntegrityError) as exc:
            raise CommandError("Check content ID and existing S3 object associations.") from exc
        self.stdout.write(f"Linked content {content_id}.")
