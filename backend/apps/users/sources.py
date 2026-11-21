import re
from uuid import uuid4

from botocore.exceptions import ClientError
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Content, UploadedSource, YouTubeContent

# The extension and upload limits are chosen by the server.
FORMATS = {
    "video/mp4": ("mp4", 1024 ** 3),
    "video/webm": ("webm", 1024 ** 3),
    "text/plain": ("txt", 2 * 1024 ** 2),
}


def storage():
    import boto3
    from botocore.config import Config
    return boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME,
                        endpoint_url=f"https://s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com",
                        config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload(request):
    mime = request.data.get("mime")
    if not isinstance(mime, str) or mime not in FORMATS:
        return Response({"detail": "MP4、WebM、UTF-8のテキストに対応しています。"}, status=400)
    extension, limit = FORMATS[mime]
    key = f"uploads/{request.user.pk}/{uuid4().hex}.{extension}"
    form = storage().generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Fields={"Content-Type": mime},
        Conditions=[{"Content-Type": mime}, ["content-length-range", 1, limit]], ExpiresIn=300,
    )
    return Response({"key": key, "form": form})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request):
    title = request.data.get("title")
    if not isinstance(title, str) or not 0 < len(title.strip()) <= 256:
        return Response({"detail": "タイトルを1〜256文字で入力してください。"}, status=400)
    details = {"title": title.strip(), "user": request.user}
    if "video_id" in request.data:
        video_id = request.data["video_id"]
        if not isinstance(video_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return Response({"detail": "YouTubeの動画IDを確認してください。"}, status=400)
        content, _ = YouTubeContent.objects.get_or_create(video_id=video_id, defaults={
            **details, "url": f"https://www.youtube.com/watch?v={video_id}"
        })
    else:
        key = request.data.get("key")
        if not isinstance(key, str) or not re.fullmatch(rf"uploads/{request.user.pk}/[0-9a-f]{{32}}\.(mp4|webm|txt)", key):
            return Response({"detail": "アップロードしたファイルを選んでください。"}, status=400)
        try:
            obj = storage().head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        except ClientError as exc:
            if exc.response["ResponseMetadata"]["HTTPStatusCode"] in (403, 404):
                return Response({"detail": "アップロードが完了していません。"}, status=400)
            raise
        mime = obj["ContentType"]
        if mime not in FORMATS or not key.endswith("." + FORMATS[mime][0]) or not 0 < obj["ContentLength"] <= FORMATS[mime][1]:
            return Response({"detail": "ファイルの形式またはサイズを確認してください。"}, status=400)
        try:
            with transaction.atomic():
                content = Content.objects.create(**details, url=settings.MEDIA_URL + key)
                UploadedSource.objects.create(content=content, key=key, mime_type=mime)
        except IntegrityError:
            content = UploadedSource.objects.select_related("content").get(key=key).content
    return Response({"id": content.pk}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def file_url(request, pk):
    source = get_object_or_404(UploadedSource, content_id=pk)
    if not (source.content.user_id == request.user.pk or
            source.content.request_set.filter(owner_id=source.content.user_id,
                                              participants=request.user).exists()):
        raise Http404
    url = storage().generate_presigned_url("get_object", Params={
        "Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": source.key,
    }, ExpiresIn=3600)
    response = HttpResponseRedirect(url)
    response["Cache-Control"] = "private, no-store"
    return response
