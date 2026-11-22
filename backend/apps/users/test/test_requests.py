from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import EmailUser, Enquete, Request, ValueType, YouTubeContent
from users.util import prepare


class RequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        prepare()
        cls.user = EmailUser.objects.create(username="owner", is_verified=True)
        cls.user.groups.add(Group.objects.get(name="Researchers"))
        cls.value_type = ValueType.objects.create(user=cls.user, title="Joy")
        cls.video = YouTubeContent.objects.create(user=cls.user, title="Video", video_id="abcdefghijk")
        cls.questions = [Enquete.objects.create(title=f"Question {i}") for i in range(3)]

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user, backend="users.cognito.SessionBackend")

    def payload(self, **kwargs):
        return {"title": "Request", "description": "text", "content": self.video.pk,
                "value_type": self.value_type.pk, "values": [{"x": 0, "y": 0}], **kwargs}

    def create(self, **kwargs):
        response = self.client.post("/api/requests/", self.payload(**kwargs), format="json")
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()

    def ids(self, data):
        return sorted(item["id"] for item in data["enquetes"])

    def test_questions_and_free_hand_are_saved(self):
        keys = [item.pk for item in self.questions[:2]]
        data = self.create(enquetes=keys, is_required_free_hand=True)
        path = f"/api/requests/{data['id']}/"
        for shown in (data, self.client.get(path).json()):
            self.assertEqual(self.ids(shown), keys)
            self.assertIs(shown["is_required_free_hand"], True)
            self.assertEqual(shown["values"], [{"x": 0, "y": 0}])
            self.assertEqual(shown["owner"]["id"], self.user.pk)
            self.assertEqual(len(shown["room_name"]), 6)
        changed = [self.questions[2].pk]
        response = self.client.put(path, self.payload(enquetes=changed, is_required_free_hand=False), format="json")
        self.assertEqual(response.status_code, 200, response.content)
        for shown in (response.json(), self.client.get(path).json()):
            self.assertEqual(self.ids(shown), changed)
            self.assertIs(shown["is_required_free_hand"], False)
        # The current edit screen does not send the questions.
        self.assertEqual(self.ids(self.client.put(path, self.payload(title="New"), format="json").json()), changed)
        self.assertEqual(self.ids(self.client.put(path, self.payload(enquetes=[]), format="json").json()), [])

    def test_the_screens_may_leave_out_the_questions(self):
        data = self.create()
        self.assertEqual(data["enquetes"], [])
        self.assertIs(data["is_required_free_hand"], False)
        response = self.client.patch(f"/api/requests/{data['id']}/", {"title": "Renamed"}, format="json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["title"], "Renamed")
        self.assertEqual(response.json()["description"], "text")

    def test_a_copy_keeps_the_questions(self):
        keys = [item.pk for item in self.questions[:2]]
        data = self.create(enquetes=keys, is_required_free_hand=True)
        person = EmailUser.objects.create(username="participant")
        Request.objects.get(pk=data["id"]).participants.add(person)
        copied = self.client.put(f"/api/requests/{data['id']}/", {"mode": "duplicate"}, format="json")
        self.assertEqual(copied.status_code, 201, copied.content)
        copied = self.client.get(f"/api/requests/{copied.json()['id']}/").json()
        self.assertNotIn(copied["id"], [data["id"]])
        self.assertNotEqual(copied["room_name"], data["room_name"])
        self.assertEqual(self.ids(copied), keys)
        self.assertIs(copied["is_required_free_hand"], True)
        self.assertEqual(copied["participants_count"], 0)
        self.assertEqual(self.ids(self.client.get(f"/api/requests/{data['id']}/").json()), keys)

    def test_fixed_fields_and_unknown_questions(self):
        data = self.create(room_name="chosen", state_processing_to_download=2)
        self.assertNotEqual(data["room_name"], "chosen")
        self.assertEqual(data["state_processing_to_download"], 0)
        self.client.put(f"/api/requests/{data['id']}/", self.payload(room_name="chosen"), format="json")
        self.assertEqual(Request.objects.get(pk=data["id"]).room_name, data["room_name"])
        response = self.client.post("/api/requests/", self.payload(enquetes=[99999]), format="json")
        self.assertEqual(response.status_code, 400)
