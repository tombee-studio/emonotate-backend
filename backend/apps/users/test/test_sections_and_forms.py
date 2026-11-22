from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import EmailUser, GoogleForm, Request, Section, ValueType, YouTubeContent
from users.util import prepare

FORM = {"title": "Form", "url": "https://docs.google.com/forms/d/e/x/viewform",
        "username_entry_field": "entry.1", "curve_id_entry_field": "entry.2"}
WEBVTT = "WEBVTT\n\n00:00:00.000 --> 00:00:10.000\nIntroduction\n"


class SectionAndFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        prepare()
        cls.owner, cls.other = (cls.person(name, "Researchers") for name in ("owner", "other"))
        cls.participant = cls.person("participant", "Guest")
        cls.guest = cls.person("guest", "Guest")
        cls.value_type = ValueType.objects.create(user=cls.owner, title="Joy")
        cls.video = YouTubeContent.objects.create(user=cls.owner, title="Video", video_id="abcdefghijk")
        cls.request = Request.objects.create(owner=cls.owner, content=cls.video, value_type=cls.value_type,
                                             title="Request", description="text", values=[])
        cls.request.participants.add(cls.participant)

    @staticmethod
    def person(name, group):
        user = EmailUser.objects.create(username=name, is_verified=True)
        user.groups.add(Group.objects.get(name=group))
        return user

    def api(self, user, **kwargs):
        client = APIClient(**kwargs)
        client.force_login(user, backend="users.cognito.SessionBackend")
        return client

    def assert_status(self, expected, response):
        self.assertEqual(response.status_code, expected, response.content)

    def cases(self):
        section = {"title": "Section", "content": self.video.pk, "webvtt": WEBVTT, "user": self.other.pk}
        yield "sections", "section", "set_section", section, Section
        yield "google_forms", "google_form", "set_google_form", FORM, GoogleForm

    def test_researchers_register_and_update_their_own(self):
        for path, key, action, data, model in self.cases():
            with self.subTest(path=path):
                api = self.api(self.owner)
                created = api.post(f"/api/{path}/", data, format="json")
                self.assert_status(201, created)
                pk = created.json()["id"]
                self.assertEqual(model.objects.get(pk=pk).user, self.owner)
                self.assert_status(200, api.put(f"/api/{action}/{self.request.pk}", {key: pk}, format="json"))
                shown = self.api(self.participant).get(f"/api/requests/{self.request.pk}/").json()
                self.assertEqual(shown[key]["title"], data["title"])
                self.assert_status(200, api.put(f"/api/{path}/{pk}/", {**data, "title": "New"}, format="json"))
                shown = self.api(self.participant).get(f"/api/requests/{self.request.pk}/").json()
                self.assertEqual(shown[key]["title"], "New")

    def test_others_cannot_change_or_use_them(self):
        for path, key, action, data, model in self.cases():
            with self.subTest(path=path):
                api = self.api(self.other)
                pk = self.api(self.owner).post(f"/api/{path}/", data, format="json").json()["id"]
                for method in ("put", "patch", "delete"):
                    self.assert_status(404, getattr(api, method)(f"/api/{path}/{pk}/", data, format="json"))
                self.assert_status(404, api.get(f"/api/{path}/{pk}/"))
                self.assertEqual(api.get(f"/api/{path}/").json()["models"], [])
                mine = Request.objects.create(owner=self.other, content=self.video, value_type=self.value_type)
                self.assert_status(404, api.put(f"/api/{action}/{mine.pk}", {key: pk}, format="json"))
                self.assert_status(404, api.put(f"/api/{action}/{self.request.pk}", {key: pk}, format="json"))
                for user in (self.participant, self.guest):
                    self.assert_status(403, self.api(user).post(f"/api/{path}/", data, format="json"))

    def test_setting_needs_a_csrf_token(self):
        api = self.api(self.owner, enforce_csrf_checks=True)
        for _, key, action, _, _ in self.cases():
            self.assertEqual(api.put(f"/api/{action}/{self.request.pk}", {key: 1}, format="json").status_code, 403)

    def test_text_without_the_webvtt_header_is_rejected(self):
        data = {"title": "Section", "content": self.video.pk, "webvtt": "text"}
        response = self.api(self.owner).post("/api/sections/", data, format="json")
        self.assert_status(400, response)
        self.assertIn("webvtt", response.json())

    def test_permissions_and_owners_reach_existing_environments(self):
        group = Group.objects.get(name="Researchers")
        group.permissions.remove(*group.permissions.filter(codename__endswith="googleform"))
        prepare()
        form, unused = GoogleForm.objects.create(**FORM), GoogleForm.objects.create(**FORM)
        self.request.google_form = form
        self.request.save()
        Request.objects.create(owner=self.other, content=self.video, value_type=self.value_type, google_form=form)
        import_module("users.migrations.0004_googleform_owners").set_owners(apps, None)
        form.refresh_from_db()
        unused.refresh_from_db()
        self.assertEqual(form.user, self.owner)
        self.assertIsNone(unused.user)
        self.assert_status(200, self.api(self.owner).put(f"/api/google_forms/{form.pk}/", FORM, format="json"))
