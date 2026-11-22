import json
import os
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import (Content, Curve, EmailUser, Enquete, EnqueteAnswer, Request, Section, UploadedSource,
                          ValueType, YouTubeContent)
from users.util import prepare

VALUES = [{"x": 0, "y": 0}, {"x": 10, "y": 1}]


class AccessTests(TestCase):
    """The rules in docs/access.md."""

    @classmethod
    def setUpTestData(cls):
        prepare()
        cls.owner = cls.person("owner", "Researchers")
        cls.researcher = cls.person("researcher", "Researchers")
        cls.relative = cls.person("relative", "Researchers")
        cls.relative.inviting_users.add(cls.owner)
        cls.participant = cls.person("participant", "Guest")
        cls.second = cls.person("second", "Guest")
        cls.guest = cls.person("guest", "Guest")
        cls.value_type = ValueType.objects.create(user=cls.owner, title="Joy")
        cls.video = YouTubeContent.objects.create(user=cls.owner, title="Video", video_id="abcdefghijk")
        cls.private = Content.objects.create(user=cls.owner, title="Private")
        UploadedSource.objects.create(content=cls.private, key="uploads/1/a.mp4", mime_type="video/mp4")
        cls.enquete = Enquete.objects.create(title="Question")
        cls.request = Request.objects.create(owner=cls.owner, content=cls.private, value_type=cls.value_type,
                                             title="Request", description="text", values=[])
        cls.request.enquetes.add(cls.enquete)
        cls.request.participants.add(cls.participant, cls.second)

    @staticmethod
    def person(name, group):
        user = EmailUser.objects.create(username=name, email=f"{name}@example.org", is_verified=True)
        user.groups.add(Group.objects.get(name=group))
        return user

    def api(self, user):
        client = APIClient()
        client.force_login(user, backend="users.cognito.SessionBackend")
        return client

    def curve(self, user, **kwargs):
        return Curve.objects.create(**{"user": user, "content": self.video, "value_type": self.value_type,
                                       "values": VALUES, "version": "arc-1", **kwargs})

    def payload(self, **kwargs):
        return {"content": self.private.pk, "value_type": self.value_type.pk, "values": VALUES, "version": "arc-1",
                "room_name": self.request.room_name, "locked": True, "kind": 2, **kwargs}

    def assert_status(self, expected, response):
        self.assertEqual(response.status_code, expected, response.content)

    def test_users_see_only_their_own_account(self):
        for user in (self.guest, self.researcher):
            api = self.api(user)
            data = api.get("/api/users/").json()
            self.assertEqual([item["id"] for item in data["models"]], [user.pk])
            self.assert_status(404, api.get(f"/api/users/{self.owner.pk}/"))
            for method in (api.put, api.patch, api.delete):
                self.assert_status(403, method(f"/api/users/{user.pk}/", {}, format="json"))
        self.assertEqual(self.api(self.guest).get("/api/me/").json()["email"], "guest@example.org")

    def test_addresses_are_hidden_from_other_users(self):
        self.curve(self.participant)
        for path in ("/api/requests/", f"/api/requests/{self.request.pk}/", "/api/requests/?role=participant",
                     "/api/contents/", "/api/youtube/", "/api/valuetypes/", "/history/curves/"):
            with self.subTest(path=path):
                response = self.api(self.participant).get(path)
                self.assert_status(200, response)
                self.assertNotIn("@example.org", response.content.decode())
                self.assertNotIn("is_superuser", response.content.decode())
        data = self.api(self.owner).get(f"/api/requests/{self.request.pk}/").json()
        self.assertEqual({item["email"] for item in data["participants"]},
                         {"participant@example.org", "second@example.org"})
        people = self.api(self.owner).get(f"/api/participants/{self.request.pk}").json()["participants"]
        self.assertEqual(set(people[0]), {"id", "username", "email"})
        self.assert_status(404, self.api(self.researcher).get(f"/api/participants/{self.request.pk}"))
        related = self.api(self.relative).get("/api/relative_users/").json()["users"]
        self.assertEqual(set(related[0]), {"id", "username", "email"})

    def test_requests_are_read_by_owner_participants_and_relatives(self):
        path = f"/api/requests/{self.request.pk}/"
        for user, expected in ((self.owner, 200), (self.participant, 200), (self.relative, 200),
                               (self.researcher, 404), (self.guest, 404)):
            with self.subTest(user=user):
                self.assert_status(expected, self.api(user).get(path))
                listed = [item["id"] for item in self.api(user).get("/api/requests/").json()["models"]]
                self.assertEqual(listed, [self.request.pk] if expected == 200 else [])
        self.assertEqual(len(self.api(self.relative).get("/api/requests/?role=relative").json()["models"]), 1)
        for user in (self.participant, self.guest):
            self.assert_status(403, self.api(user).delete(path))
        for user in (self.relative, self.researcher):
            self.assert_status(404, self.api(user).delete(path))
            self.assert_status(404, self.api(user).put(path, {"mode": "duplicate"}, format="json"))
        self.assert_status(204, self.api(self.owner).delete(path))

    def test_requests_use_readable_contents(self):
        data = {"content": self.private.pk, "value_type": self.value_type.pk, "title": "New", "values": [],
                "description": "text", "owner": self.owner.pk, "is_required_free_hand": False}
        self.assert_status(400, self.api(self.researcher).post("/api/requests/", data, format="json"))
        data["content"] = self.video.pk
        created = self.api(self.researcher).post("/api/requests/", data, format="json")
        self.assert_status(201, created)
        self.assertEqual(created.json()["owner"]["id"], self.researcher.pk)
        self.assert_status(403, self.api(self.guest).post("/api/requests/", data, format="json"))
        path = f"/api/requests/{self.request.pk}/"
        data["content"] = self.private.pk
        self.assert_status(200, self.api(self.owner).put(path, data, format="json"))

    def test_uploads_are_read_by_owner_and_participants(self):
        path = f"/api/contents/{self.private.pk}/"
        # Someone else's request must not open the upload.
        forged = Request.objects.create(owner=self.researcher, content=self.private, value_type=self.value_type,
                                        title="Forged", values=[])
        forged.participants.add(self.researcher)
        for user, expected in ((self.owner, 200), (self.participant, 200), (self.researcher, 404),
                               (self.relative, 404), (self.guest, 404)):
            with self.subTest(user=user):
                self.assert_status(expected, self.api(user).get(path))
        self.assert_status(200, self.api(self.guest).get(f"/api/contents/{self.video.pk}/"))

    def test_only_participants_answer_a_request(self):
        for user, expected in ((self.owner, 201), (self.participant, 201)):
            self.assert_status(expected, self.api(user).post("/api/curves/", self.payload(), format="json"))
        for user in (self.guest, self.researcher, self.relative):
            with self.subTest(user=user):
                api = self.api(user)
                self.assert_status(400, api.post("/api/curves/", self.payload(), format="json"))
                public = self.payload(content=self.video.pk)
                self.assert_status(403, api.post("/api/curves/", public, format="json"))
                own = self.payload(content=self.video.pk, room_name="own", locked=False)
                saved = api.post("/api/curves/", own, format="json")
                self.assert_status(201, saved)
                url = f"/api/curves/{saved.json()['id']}/"
                self.assert_status(403, api.patch(url, {"room_name": self.request.room_name}, format="json"))
        self.assertEqual(Curve.objects.filter(room_name=self.request.room_name).count(), 2)

    def test_curves_belong_to_their_author_and_locked_ones_stay(self):
        locked, draft = self.curve(self.participant), self.curve(self.participant, locked=False)
        for user in (self.owner, self.second):
            for curve in (locked, draft):
                for method in ("get", "patch", "delete"):
                    self.assert_status(404, getattr(self.api(user), method)(f"/api/curves/{curve.pk}/"))
        api = self.api(self.participant)
        self.assert_status(403, api.delete(f"/api/curves/{locked.pk}/"))
        self.assert_status(403, api.patch(f"/api/curves/{locked.pk}/", {"locked": False}, format="json"))
        self.assert_status(204, api.delete(f"/api/curves/{draft.pk}/"))
        forged = api.post("/api/curves/", self.payload(user=self.second.pk), format="json")
        self.assertEqual(forged.json()["user"]["id"], self.participant.pk)

    def test_only_the_owner_changes_shared_items(self):
        for path, data in ((f"/api/valuetypes/{self.value_type.pk}/", {"title": "Changed"}),
                           (f"/api/youtube/{self.video.pk}/", {"title": "Changed"}),
                           (f"/api/contents/{self.video.pk}/", {"title": "Changed"})):
            with self.subTest(path=path):
                self.assert_status(200, self.api(self.researcher).get(path))
                self.assert_status(404, self.api(self.researcher).patch(path, data, format="json"))
                self.assert_status(404, self.api(self.researcher).delete(path))
                self.assert_status(200, self.api(self.owner).patch(path, data, format="json"))
        created = self.api(self.researcher).post("/api/valuetypes/", {"title": "New", "user": self.owner.pk},
                                                 format="json")
        self.assertEqual(created.json()["user"]["id"], self.researcher.pk)
        created = self.api(self.guest).post("/api/youtube/", {"title": "New", "video_id": "kjihgfedcba",
                                                              "url": "https://www.youtube.com/watch?v=kjihgfedcba",
                                                              "user": self.owner.pk}, format="json")
        self.assert_status(201, created)
        self.assertEqual(created.json()["user"]["id"], self.guest.pk)

    def test_items_used_by_others_are_kept(self):
        self.curve(self.participant)
        api = self.api(self.owner)
        for path in (f"/api/valuetypes/{self.value_type.pk}/", f"/api/youtube/{self.video.pk}/",
                     f"/api/contents/{self.video.pk}/"):
            self.assert_status(403, api.delete(path))
        unused = ValueType.objects.create(user=self.owner, title="Unused")
        self.assert_status(204, api.delete(f"/api/valuetypes/{unused.pk}/"))
        path = f"/api/enquetes/{self.enquete.pk}/"
        self.assert_status(403, self.api(self.researcher).delete(path))
        self.assert_status(403, self.api(self.researcher).patch(path, {"title": "x"}, format="json"))
        self.assert_status(200, api.patch(path, {"title": "Better question"}, format="json"))
        EnqueteAnswer.objects.create(curve=Curve.objects.get(), enquete=self.enquete, answer="yes")
        self.assert_status(403, api.delete(path))

    def test_sections_use_readable_contents(self):
        admin = EmailUser.objects.create(username="admin", is_superuser=True, is_verified=True)
        data = {"title": "Section", "content": self.private.pk, "webvtt": "WEBVTT"}
        self.assert_status(400, self.api(admin).post("/api/sections/", data, format="json"))
        created = self.api(admin).post("/api/sections/", {**data, "content": self.video.pk}, format="json")
        self.assert_status(201, created)
        self.assertEqual(created.json()["user"], admin.pk)

    def test_sections_are_attached_by_their_owner(self):
        section = Section.objects.create(user=self.researcher, content=self.video, title="Section")
        path = f"/api/set_section/{self.request.pk}"
        self.api(self.owner).put(path, {"section": section.pk}, format="json")
        self.request.refresh_from_db()
        self.assertIsNone(self.request.section)
        section.user = self.owner
        section.save()
        self.api(self.owner).put(path, {"section": section.pk}, format="json")
        self.request.refresh_from_db()
        self.assertEqual(self.request.section, section)

    @patch.dict(os.environ, {"STAGE": "AWS"})
    def test_input_screens_follow_the_request_rules(self):
        self.request.content = self.video
        self.request.description = "</script><script>alert(1)</script>"
        self.request.save()
        for screen in ("free-hand", "fold-line"):
            path = f"/{screen}/?request={self.request.pk}"
            for user, expected in ((self.owner, 200), (self.participant, 200), (self.guest, 404),
                                   (self.researcher, 404)):
                self.assertEqual(self.api(user).get(path).status_code, expected)
            page = self.api(self.participant).get(path).content.decode()
            self.assertNotIn("<script>alert", page)
            self.assertNotIn("second@example.org", page)
            page = self.api(self.guest).get(f"/{screen}/", {
                "video_id": 'x";alert(1)//\\', "room_name": "</script><script>alert(1)</script>"}).content.decode()
            self.assertNotIn("<script>alert", page)
            self.assertNotIn('";alert', page)
            self.assertEqual(self.api(self.guest).get(f"/{screen}/?request=x").status_code, 404)

    @patch("users.views.storage")
    def test_export_is_for_the_owner(self, storage):
        storage.return_value.generate_presigned_url.return_value = "https://example.org/file"
        self.curve(self.participant, room_name=self.request.room_name)
        path = f"/api/get_download_curve_data/{self.request.pk}"
        for user in (self.participant, self.researcher, self.relative, self.guest):
            self.assertEqual(self.api(user).get(path).status_code, 404)
        self.assertEqual(self.api(self.owner).get(path).status_code, 200)
        exported = json.loads(storage.return_value.put_object.call_args.kwargs["Body"])
        self.assertEqual(exported[0]["user"], {"id": self.participant.pk, "username": "participant",
                                               "email": "participant@example.org"})

    def test_mail_needs_post_and_removed_endpoints_are_gone(self):
        api = self.api(self.owner)
        self.assertEqual(api.get(f"/api/send/{self.request.pk}").status_code, 405)
        self.assertEqual(api.get(f"/api/reset_email_addresses/{self.request.pk}").status_code, 404)
        self.assertEqual(api.get("/api/curves_with_youtube/").status_code, 404)
