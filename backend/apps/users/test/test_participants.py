from uuid import uuid4

from django.contrib.auth.models import Group
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from users.models import CognitoIdentity, EmailUser, RelationParticipant, Request, ValueType, YouTubeContent
from users.util import prepare


class ParticipantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        prepare()
        cls.owner = EmailUser.objects.create(username="owner", is_verified=True)
        cls.owner.groups.add(Group.objects.get(name="Researchers"))
        value_type = ValueType.objects.create(user=cls.owner, title="Joy")
        video = YouTubeContent.objects.create(user=cls.owner, title="Video", video_id="abcdefghijk")
        cls.request = Request.objects.create(owner=cls.owner, content=video, value_type=value_type, title="Request")
        cls.other = Request.objects.create(owner=cls.owner, content=video, value_type=value_type, title="Other")

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.owner, backend="users.cognito.SessionBackend")
        self.path = f"/api/participants/{self.request.pk}"

    def add(self, emails):
        return self.client.post(self.path, {"emails": emails}, format="json")

    def emails(self, count, start=0):
        return [f"p{i:04}@example.org" for i in range(start, start + count)]

    def test_500_participants_are_registered_listed_and_removed(self):
        response = self.add(self.emails(500))
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json(), {"added": 500, "total": 500})
        # Again, with one more: nobody is added twice.
        self.assertEqual(self.add(self.emails(501)).json(), {"added": 1, "total": 501})
        data = self.client.get(self.path, {"page_size": 50, "page": 11}).json()
        self.assertEqual(data["pagination"]["total_entries"], 501)
        self.assertEqual(data["pagination"]["total_pages"], 11)
        self.assertEqual([row["email"] for row in data["models"]], ["p0500@example.org"])
        found = self.client.get(self.path, {"search": "P012"}).json()["models"]
        self.assertEqual([row["email"] for row in found], self.emails(10, 120))
        detail = self.client.get(f"/api/requests/{self.request.pk}/").json()
        self.assertEqual(detail["participants_count"], 501)
        ids = [row["id"] for row in found]
        removed = self.client.delete(self.path, {"ids": ids}, format="json")
        self.assertEqual(removed.json(), {"total": 491})
        self.assertEqual(EmailUser.objects.filter(pk__in=ids).count(), 10)

    def test_queries_do_not_grow_with_the_participants(self):
        def count(call):
            with CaptureQueriesContext(connection) as queries:
                call()
            return len(queries)
        small = count(lambda: self.add(self.emails(5)))
        large = count(lambda: self.add(self.emails(60, 100)))
        self.assertEqual(small, large)
        listed = [count(lambda: self.client.get(self.path, {"page_size": size})) for size in (5, 60)]
        self.assertEqual(listed[0], listed[1])

    def test_existing_accounts_are_reused(self):
        placeholder = EmailUser.objects.create(username="old", email="same@example.org")
        account = EmailUser.objects.create(username="account", email="same@example.org")
        CognitoIdentity.objects.create(user=account, pool_id="pool", subject=uuid4())
        self.assertEqual(self.add(["same@Example.org", " same@example.org "]).json(), {"added": 1, "total": 1})
        self.assertEqual(self.request.participants.get(), account)
        self.assertFalse(RelationParticipant.objects.filter(user=placeholder).exists())
        self.add(["new@example.org"])
        created = EmailUser.objects.get(email="new@example.org")
        self.assertFalse(created.has_usable_password())
        self.assertEqual({group.name for group in created.groups.all()}, {"Guest", "General"})

    def test_input_is_checked(self):
        for emails in (None, "a@example.org", [], [1], ["a@example.org"] * 1001):
            self.assertEqual(self.add(emails).status_code, 400)
        response = self.add(["ok@example.org", "broken", "x@"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["invalid"], ["broken", "x@"])
        self.assertFalse(self.request.participants.exists())
        for ids in (None, "1", ["1"], [True]):
            self.assertEqual(self.client.delete(self.path, {"ids": ids}, format="json").status_code, 400)

    def test_only_this_request_changes(self):
        self.add(self.emails(1))
        user = self.request.participants.get()
        self.other.participants.add(user)
        self.client.delete(self.path, {"ids": [user.pk]}, format="json")
        self.assertEqual(self.other.participants.get(), user)
        stranger = EmailUser.objects.create(username="stranger", is_verified=True)
        stranger.groups.add(Group.objects.get(name="Researchers"))
        client = APIClient()
        client.force_login(stranger, backend="users.cognito.SessionBackend")
        for method, data in (("get", None), ("post", {"emails": self.emails(1)}), ("delete", {"ids": [user.pk]})):
            self.assertEqual(getattr(client, method)(self.path, data, format="json").status_code
                             if data else client.get(self.path).status_code, 404)
        strict = APIClient(enforce_csrf_checks=True)
        strict.force_login(self.owner, backend="users.cognito.SessionBackend")
        self.assertEqual(strict.post(self.path, {"emails": self.emails(1)}, format="json").status_code, 403)
