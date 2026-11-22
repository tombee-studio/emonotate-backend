from datetime import datetime, timedelta
from threading import Barrier, Thread
from unittest import skipUnless

from django.contrib.auth.models import Group
from django.db import connection
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from users.models import Curve, EmailUser, Request, ValueType, YouTubeContent
from users.util import prepare


class Fixture:
    def prepare_data(self):
        prepare()
        self.owner, self.participant = (EmailUser.objects.create(username=name, is_verified=True)
                                        for name in ("owner", "participant"))
        self.owner.groups.add(Group.objects.get(name="Researchers"))
        self.participant.groups.add(Group.objects.get(name="Guest"))
        self.value_type = ValueType.objects.create(user=self.owner, title="Joy")
        self.video = YouTubeContent.objects.create(user=self.owner, title="Video", video_id="abcdefghijk")
        self.request = Request.objects.create(owner=self.owner, content=self.video, value_type=self.value_type,
                                              title="Request", description="text", values=[])
        self.request.participants.add(self.participant)

    def api(self, user):
        client = APIClient()
        client.force_login(user, backend="users.cognito.SessionBackend")
        return client

    def set(self, **kwargs):
        Request.objects.filter(pk=self.request.pk).update(**kwargs)

    def submit(self, user=None, **kwargs):
        return self.api(user or self.participant).post("/api/curves/", {
            "content": self.video.pk, "value_type": self.value_type.pk, "version": "arc-1", "kind": 2,
            "values": [{"x": 0, "y": 0}, {"x": 1, "y": 1}], "room_name": self.request.room_name,
            "locked": True, **kwargs}, format="json")


class AcceptanceTests(Fixture, TestCase):
    def setUp(self):
        self.prepare_data()
        self.now = datetime.now().replace(microsecond=0)

    def detail(self, user=None):
        return self.api(user or self.participant).get(f"/api/requests/{self.request.pk}/").json()

    def test_there_is_no_limit_by_default(self):
        for _ in range(3):
            self.assertEqual(self.submit().status_code, 201)
        self.assertIsNone(self.detail()["closed_reason"])

    def test_answers_outside_the_period_are_rejected_with_the_reason(self):
        hour = timedelta(hours=1)
        for starts_at, ends_at, reason in (
                (self.now + hour, None, f"受付は {self.now + hour:%Y/%m/%d %H:%M} からです。"),
                (None, self.now - hour, f"受付は {self.now - hour:%Y/%m/%d %H:%M} に終了しました。"),
                (self.now - hour, self.now + hour, None)):
            with self.subTest(reason=reason):
                self.set(starts_at=starts_at, ends_at=ends_at)
                self.assertEqual(self.detail()["closed_reason"], reason)
                for user in (self.participant, self.owner):
                    response = self.submit(user)
                    self.assertEqual(response.status_code, 403 if reason else 201, response.content)
                    if reason:
                        self.assertEqual(response.json()["detail"], reason)

    def test_answers_over_the_count_are_rejected(self):
        self.set(max_submissions=2)
        self.assertEqual([self.submit().status_code for _ in range(3)], [201, 201, 403])
        self.assertEqual(self.submit().json()["detail"], "提出できる回数(2回)に達しています。")
        self.assertEqual(self.detail()["closed_reason"], "提出できる回数(2回)に達しています。")
        self.assertIsNone(self.detail(self.owner)["closed_reason"])
        self.assertEqual(self.submit(self.owner).status_code, 201)
        # Curves that answer no request are free.
        self.assertEqual(self.submit(room_name="own").status_code, 201)

    def test_updates_follow_the_same_rules(self):
        self.set(max_submissions=1)
        api = self.api(self.participant)
        draft = f"/api/curves/{self.submit(locked=False).json()['id']}/"
        other = f"/api/curves/{self.submit(room_name='own', locked=False).json()['id']}/"
        values = {"values": [{"x": 0, "y": 1}, {"x": 1, "y": 1}]}
        self.assertEqual(api.patch(draft, values, format="json").status_code, 200)
        self.assertEqual(api.patch(other, {"room_name": self.request.room_name}, format="json").status_code, 403)
        self.set(ends_at=self.now - timedelta(minutes=1))
        self.assertEqual(api.patch(draft, values, format="json").status_code, 403)
        self.assertEqual(api.patch(other, values, format="json").status_code, 200)

    def test_owner_sets_and_clears_the_limits(self):
        path, api = f"/api/requests/{self.request.pk}/", self.api(self.owner)
        data = {"starts_at": "2026-12-01T09:00", "ends_at": "2026-12-31T18:00", "max_submissions": 1}
        response = api.patch(path, data, format="json")
        self.assertEqual(response.status_code, 200, response.content)
        shown = api.get(path).json()
        self.assertEqual((shown["starts_at"], shown["ends_at"], shown["max_submissions"]),
                         ("2026-12-01T09:00:00", "2026-12-31T18:00:00", 1))
        for wrong in ({"ends_at": "2026-12-01T09:00"}, {"max_submissions": 0}, {"max_submissions": -1},
                      {"starts_at": "soon"}):
            self.assertEqual(api.patch(path, wrong, format="json").status_code, 400, wrong)
        cleared = {"starts_at": None, "ends_at": None, "max_submissions": None}
        self.assertEqual(api.patch(path, cleared, format="json").status_code, 200)
        self.assertEqual({name: api.get(path).json()[name] for name in cleared}, cleared)

    def test_other_rules_still_apply(self):
        stranger = EmailUser.objects.create(username="stranger", is_verified=True)
        stranger.groups.add(Group.objects.get(name="Guest"))
        self.assertEqual(self.submit(stranger).status_code, 403)


@skipUnless(connection.vendor == "postgresql", "SQLite has no row locks")
class SimultaneousSubmissionTests(Fixture, TransactionTestCase):
    def test_the_count_holds(self):
        self.prepare_data()
        self.set(max_submissions=2)
        barrier, statuses = Barrier(8), []

        def submit():
            barrier.wait()
            statuses.append(self.submit().status_code)
            connection.close()

        threads = [Thread(target=submit) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sorted(statuses), [201] * 2 + [403] * 6)
        self.assertEqual(Curve.objects.count(), 2)
