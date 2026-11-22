import json

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import Content, Curve, EmailUser, UploadedSource, ValueType, YouTubeContent
from users.util import prepare


class CurveValuesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        prepare()
        cls.user = EmailUser.objects.create(username="user", is_verified=True)
        cls.user.groups.add(Group.objects.get(name="Guest"))
        cls.value_type = ValueType.objects.create(user=cls.user, title="Joy")
        cls.video = YouTubeContent.objects.create(user=cls.user, title="Video", video_id="abcdefghijk")
        cls.text = Content.objects.create(user=cls.user, title="Text")
        UploadedSource.objects.create(content=cls.text, key="uploads/1/a.txt", mime_type="text/plain")

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user, backend="users.cognito.SessionBackend")

    def save(self, values, content=None, version="arc-1", kind=2, **kwargs):
        return self.client.post("/api/curves/", {
            "content": (content or self.video).pk, "value_type": self.value_type.pk, "values": values,
            "version": version, "kind": kind, "room_name": "own", "locked": False, **kwargs}, format="json")

    def test_current_formats_are_saved(self):
        free_hand = [{"x": i * 0.1, "y": 0.5} for i in range(5000)]
        fold_line = [{"x": 0, "y": 0, "axis": "v", "index": 0}, {"x": 30.5, "y": 0.4, "axis": "vh", "index": 1},
                     {"x": 60.2, "y": 1, "axis": "v", "index": 2}]
        react = [{"x": 0, "y": -1, "axis": "v", "type": "fixed", "state": "start"},
                 {"x": 5.25, "y": 0.5, "axis": "hv", "type": "custom", "state": "middle"},
                 {"x": 5.25, "y": 1, "axis": "hv", "type": "custom", "state": "middle"},
                 {"x": 100, "y": 1, "axis": "v", "type": "fixed", "state": "end"}]
        for values, content, version, kind in (
                (free_hand, self.video, "1.0.0", 1), (fold_line, self.video, "1.0.0", 2),
                (react, self.video, "arc-1", 2), (react, self.text, "arc-1", 2)):
            response = self.save(values, content, version, kind)
            self.assertEqual(response.status_code, 201, response.content)
            self.assertEqual(Curve.objects.get(pk=response.json()["id"]).values, values)

    def test_old_screens_may_overshoot_the_edge(self):
        values = [{"x": -0.1, "y": 1.003}, {"x": 60, "y": -0.003}]
        self.assertEqual(self.save(values, version="1.0.0", kind=1).json()["values"],
                         [{"x": 0, "y": 1}, {"x": 60, "y": -0.003}])
        self.assertEqual(self.save(values).status_code, 400)
        self.assertEqual(self.save([{"x": -30, "y": 0}, {"x": 60, "y": 0}], version="1.0.0").status_code, 400)
        self.assertEqual(self.save([{"x": 0, "y": 1.2}, {"x": 60, "y": 0}], version="1.0.0").status_code, 400)

    def test_invalid_values_are_rejected(self):
        good = {"x": 0, "y": 0}
        for values in (
                None, "text", {}, 1, [], [good], [good, 1], [good, [1, 1]], [good, {}], [good, {"x": 1}],
                [good, {"x": "1", "y": 0}], [good, {"x": True, "y": 0}], [good, {"x": None, "y": 0}],
                [good, {"x": 1, "y": 1.01}], [good, {"x": 1, "y": -1.01}], [{"x": -1, "y": 0}, good],
                [good, {"x": 86401, "y": 0}], [{"x": 2, "y": 0}, {"x": 1, "y": 0}, {"x": 3, "y": 0}],
                [good, good], [good, {"x": 1, "y": 0, "axis": {}}], [good, {"x": 1, "y": 0, "type": "a" * 1001}],
                [{"x": i / 100, "y": 0} for i in range(20001)]):
            with self.subTest(values=str(values)[:60]):
                response = self.save(values)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn("values", response.json())
        self.assertEqual(self.save([good, {"x": 100.5, "y": 0}], self.text).status_code, 400)
        for number in ("NaN", "Infinity", "1e999"):
            body = json.dumps({"content": self.video.pk, "value_type": self.value_type.pk, "version": "arc-1",
                               "values": [good, {"x": 1, "y": 0}]}).replace('"x": 1,', f'"x": {number},')
            response = self.client.post("/api/curves/", body, content_type="application/json")
            self.assertEqual(response.status_code, 400, number)
        self.assertFalse(Curve.objects.exists())

    def test_updates_are_checked(self):
        url = f"/api/curves/{self.save([{'x': 0, 'y': 0}, {'x': 1, 'y': 0}]).json()['id']}/"
        self.assertEqual(self.client.patch(url, {"values": [{"x": 0, "y": 5}]}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(url, {"room_name": "renamed"}, format="json").status_code, 200)
        self.assertEqual(self.client.patch(url, {"values": [{"x": 0, "y": 1}, {"x": 2, "y": 0}]},
                                           format="json").json()["values"][1]["x"], 2)
