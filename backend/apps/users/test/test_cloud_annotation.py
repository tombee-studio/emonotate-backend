import os
import re
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth.models import Group
from django.test import TestCase
from django.core.management import call_command, CommandError
from io import StringIO
from rest_framework.test import APIClient

from users.models import (CognitoIdentity, Curve, EmailUser, Request, UploadedSource, ValueType,
                          YouTubeContent)
from users.util import prepare


class CloudAnnotationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        prepare()

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.subject = str(uuid4())

    def sign_in(self, email="reader@example.org"):
        start = self.client.get("/api/cognito/login/")
        query = parse_qs(urlsplit(start.url).query)
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertNotIn("code_verifier", query)
        with patch("users.cognito.requests.post") as tokens, patch("users.cognito.requests.get") as profile:
            tokens.return_value.json.return_value = {"access_token": "test-token", "expires_in": 3600}
            profile.return_value.json.return_value = {"sub": self.subject, "email": email, "email_verified": "true"}
            response = self.client.get("/api/cognito/callback/", {"code": "code", "state": query["state"][0]})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(tokens.call_args.kwargs["data"]["code_verifier"])
        user = self.client.get("/api/me/").json()
        self.client.credentials(HTTP_X_CSRFTOKEN=self.client.cookies["csrftoken"].value)
        return user

    def test_cognito_session_uses_subject_and_rejects_bad_state(self):
        self.assertEqual(self.client.get("/api/me/").status_code, 401)
        self.client.get("/api/cognito/login/")
        with patch("users.cognito.requests.post") as exchange:
            self.assertEqual(self.client.get("/api/cognito/callback/", {"code": "x", "state": "wrong"}).status_code, 400)
            exchange.assert_not_called()
        legacy = EmailUser.objects.create_user("original", "reader@example.org")
        user = self.sign_in()
        self.assertNotEqual(user["id"], legacy.pk)
        self.assertNotIn("password", user)
        self.assertFalse(CognitoIdentity.objects.get(subject=self.subject).user.has_usable_password())
        self.assertEqual(self.client.post("/api/logout/").status_code, 200)
        self.assertEqual(self.client.get("/api/me/").status_code, 401)
        self.assertEqual(self.sign_in("updated@example.org")["id"], user["id"])
        self.assertEqual(self.client.post("/api/login/", {"password": "old"}).status_code, 404)

    def test_admin_requires_staff_cognito_session(self):
        self.assertEqual(self.client.get("/admin/").status_code, 401)
        user = EmailUser.objects.get(pk=self.sign_in()["id"])
        self.assertRedirects(self.client.get("/admin/"), "/admin/login/?next=/admin/",
                             fetch_redirect_response=False)

        # A password must never open the admin, even for a superuser.
        EmailUser.objects.create_superuser("root", "root@example.org", "password")
        self.client.post("/admin/login/", {"username": "root", "password": "password"})
        self.assertEqual(self.client.get("/admin/").status_code, 302)

        user.is_staff = user.is_superuser = True
        user.save()
        self.assertEqual(self.client.get("/admin/").status_code, 200)
        self.assertEqual(self.client.get("/admin/users/emailuser/").status_code, 200)
        add = "/admin/auth/group/add/"
        self.assertEqual(self.client.post(add, {"name": "Operators"}).status_code, 302)
        self.assertTrue(Group.objects.filter(name="Operators").exists())
        self.client.credentials()
        self.assertEqual(self.client.post(add, {"name": "Forged"}).status_code, 403)

    def test_admin_assets_are_served_below_admin(self):
        response = self.client.get("/admin/static/admin/css/base.css")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/css"))
        response.close()

    @patch.dict(os.environ, {"STAGE": "AWS"})
    def test_input_screens_load_scripts_from_the_frontend(self):
        user = EmailUser.objects.get(pk=self.sign_in()["id"])
        content = YouTubeContent.objects.create(user=user, title="A video", video_id="abcdefghijk")
        value_type = ValueType.objects.create(user=user, title="Joy")
        item = Request.objects.create(owner=user, content=content, value_type=value_type, title="A request",
                                      values=[])
        curve = Curve.objects.create(user=user, content=content, value_type=value_type, version="1.0.0",
                                     values=[{"x": 0, "y": 0}, {"x": 1, "y": 1}])
        for screen, scripts in (
                ("free-hand", ["utils", "MyYouTubeView", "GraphView", "FreeHandInputField",
                               "ButtonAction", "ValueTypeList"]),
                ("fold-line", ["utils", "MyYouTubeView", "FoldLineGraphView", "FoldLineInputField",
                               "ButtonAction", "ValueTypeList"])):
            for path in (f"/{screen}/?request={item.pk}", f"/{screen}/?video_id=abcdefghijk",
                         f"/{screen}/{curve.pk}"):
                with self.subTest(path=path):
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200)
                    # CloudFront serves /static/* from the emonotate-app bucket.
                    local = re.findall(r'<script src="(/[^"]*)"', response.content.decode())
                    self.assertEqual(local, [f"/static/users/js/{name}.js" for name in scripts])

    def test_restored_user_binding_is_idempotent(self):
        user = EmailUser.objects.create_user("restored", "reader@example.org")
        for _ in range(2):
            call_command("link_cognito_user", str(user.pk), self.subject, stdout=StringIO())
        other = EmailUser.objects.create_user("different", "different@example.org")
        with self.assertRaises(CommandError):
            call_command("link_cognito_user", str(other.pk), self.subject, stdout=StringIO())
        self.assertEqual(self.sign_in()["id"], user.pk)

    def test_writes_require_session_and_csrf(self):
        data = {"title": "A video", "video_id": "abcdefghijk"}
        self.assertEqual(self.client.post("/api/sources/", data, format="json").status_code, 401)
        self.sign_in()
        self.client.credentials()
        self.assertEqual(self.client.post("/api/sources/", data, format="json").status_code, 403)

    @patch("users.sources.storage")
    def test_all_sources_save_reopen_edit_and_file_ownership(self, storage):
        s3 = storage.return_value
        s3.generate_presigned_post.return_value = {"url": "https://example.org", "fields": {}}
        s3.generate_presigned_url.return_value = "https://example.org/private"
        user = self.sign_in()
        other = EmailUser.objects.create_user("other", "other@example.org")
        stranger = APIClient()
        stranger.force_login(other, backend="users.cognito.SessionBackend")
        for mime in ("youtube", "video/mp4", "text/plain"):
            data = {"title": mime}
            if mime == "youtube":
                data["video_id"] = "abcdefghijk"
            else:
                form = self.client.post("/api/sources/upload/", {"mime": mime}, format="json")
                self.assertEqual(form.status_code, 200)
                data["key"] = form.json()["key"]
                conditions = s3.generate_presigned_post.call_args.kwargs["Conditions"]
                self.assertIn({"Content-Type": mime}, conditions)
                self.assertFalse(any("acl" in c for c in conditions))
                s3.head_object.return_value = {"ContentType": mime, "ContentLength": 12}
                self.assertEqual(stranger.post("/api/sources/", data, format="json").status_code, 400)
            created = self.client.post("/api/sources/", data, format="json")
            self.assertEqual(created.status_code, 201, created.content)
            pk = created.json()["id"]
            detail = self.client.get(f"/api/contents/{pk}/").json()
            if mime != "youtube":
                self.assertEqual(self.client.post("/api/sources/", data, format="json").json()["id"], pk)
                self.assertEqual(self.client.get(detail["url"]).url, "https://example.org/private")
                self.assertEqual(stranger.get(detail["url"]).status_code, 404)
            values = [{"x": 0, "y": 0}, {"x": 100, "y": 1}]
            payload = {"content": pk, "user": other.pk, "value_type": user["default_value_type"]["id"],
                       "values": values, "room_name": f"content-{pk}", "locked": False, "kind": 2, "version": "arc-1"}
            saved = self.client.post("/api/curves/", payload, format="json")
            self.assertEqual(saved.status_code, 201, saved.content)
            curve_url = f"/api/curves/{saved.json()['id']}/"
            self.assertEqual(self.client.get(curve_url).json()["values"], values)
            self.assertEqual(saved.json()["user"]["id"], user["id"])
            values[-1]["y"] = -1
            self.assertEqual(self.client.put(curve_url, payload, format="json").json()["values"], values)
        self.assertEqual(UploadedSource.objects.count(), 2)
        self.assertEqual(Curve.objects.filter(user_id=user["id"]).count(), 3)
        self.assertEqual(len(self.client.get("/history/curves/").json()["models"]), 3)
