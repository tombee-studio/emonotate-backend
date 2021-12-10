import factory
import json
import random

from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.test.factory import *
from users.models import *
from users.views import *
from faker import Faker
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory, force_authenticate

from users import views


def convert_to_dict_from(model):
    data = { key: value if type(value) is str or type(value) is int else str(value)
        for key, value in model.__dict__.items() if key is not '_state' and value is not None }
    return data


class EmailUserTestCase(TestCase):
    def test_create_generaluser(self):
        faker = Faker()
        username = faker.name()
        email = faker.email()
        user = EmailUser.objects.create_user(
            username=username, email=email, password=faker.password())
        self.assertEqual(user.username, username)
        for perm in ['users.add_request', 'users.add_content', 'users.add_emailuser']:
            self.assertEqual(user.has_perm(perm), False)
    
    def test_create_researcher(self):
        faker = Faker()
        username = faker.name()
        email = faker.email()
        user = EmailUser.objects.create_researcher(
            username=username, email=email, password=faker.password())
        self.assertEqual(user.username, username)
        for perm in ['users.add_request', 'users.add_content', 'users.add_emailuser']:
            self.assertEqual(user.has_perm(perm), True)
        

class EmailUserSignUpTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_object = EmailUserFactory.build()
        cls.user_saved = EmailUserFactory.create()
        cls.client = APIClient()
        cls.signup_url = reverse('signup')
        cls.faker_obj = Faker()

    def test_if_data_is_correct_then_signup(self):
        signup_dict = {
            'username': self.user_object.username,
            'password1': 'password',
            'password2': 'password',
            'email': self.user_object.email,
        }
        response = self.client.post(self.signup_url, signup_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_username_already_exists_dont_signup(self):
        # Prepare data with already saved user
        signup_dict = {
            'username': self.user_saved.username,
            'password1': 'password',
            'password2': 'password',
            'email': self.user_saved.email,
        }
        response = self.client.post(self.signup_url, signup_dict)


class ContentAPITestCase(APITestCase):
    def test_get_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 200],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            request = api.get('/api/contents/', format='json')
            force_authenticate(request, user=user)
            view = ContentViewSet.as_view({'get': 'list'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content_object = ContentFactory.build()

            data = convert_to_dict_from(content_object)
            request = api.post('/api/contents/', data, format='json')
            force_authenticate(request, user=user)
            view = ContentViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_put_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content_object = ContentFactory.create()

            data = convert_to_dict_from(content_object)
            data['title'] = Faker().word()
            request = api.put("/api/contents/{content_object.id}/", 
                data, format='json')
            force_authenticate(request, user=user)
            view = ContentViewSet.as_view({'put': 'update'})
            response = view(request, pk=content_object.id)
            self.assertEqual(response.status_code, status)

    def test_delete_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 204], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 204]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content_object = ContentFactory.create()

            data = convert_to_dict_from(content_object)
            request = api.delete("/api/contents/{content_object.id}/", format='json')
            force_authenticate(request, user=user)
            view = ContentViewSet.as_view({'delete': 'destroy'})
            response = view(request, pk=content_object.id)
            self.assertEqual(response.status_code, status)


class YouTubeContentAPITestCase(APITestCase):
    def test_get_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 200],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            request = api.get('/api/contents/', format='json')
            force_authenticate(request, user=user)
            view = ValueTypeViewSet.as_view({'get': 'list'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            obj = ValueTypeFactory.build()

            data = convert_to_dict_from(obj)
            request = api.post('/api/value_type/', data, format='json')
            force_authenticate(request, user=user)
            view = ValueTypeViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_put_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            obj = ValueTypeFactory.create()

            data = convert_to_dict_from(obj)
            data['title'] = Faker().word()
            request = api.put("/api/value_type/{obj.id}/", 
                data, format='json')
            force_authenticate(request, user=user)
            view = ValueTypeViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)

    def test_delete_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 204], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 204]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            obj = ValueTypeFactory.create()

            data = convert_to_dict_from(obj)
            request = api.delete("/api/contents/{obj.id}/", format='json')
            force_authenticate(request, user=user)
            view = ValueTypeViewSet.as_view({'delete': 'destroy'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)


class ContentAPITestCase(APITestCase):
    def test_get_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 200],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            request = api.get('/api/youtube/', format='json')
            force_authenticate(request, user=user)
            view = YouTubeContentViewSet.as_view({'get': 'list'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            obj = YouTubeContentFactory.build()

            data = convert_to_dict_from(obj)
            request = api.post('/api/youtube/', data, format='json')
            force_authenticate(request, user=user)
            view = YouTubeContentViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_put_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            obj = YouTubeContentFactory.create()

            data = convert_to_dict_from(obj)
            data['title'] = Faker().word()
            request = api.put("/api/youtube/{obj.id}/", 
                data, format='json')
            force_authenticate(request, user=user)
            view = YouTubeContentViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)

    def test_delete_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 204], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 204]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            obj = YouTubeContentFactory.create()

            data = convert_to_dict_from(obj)
            request = api.delete("/api/youtube/{obj.id}/", format='json')
            force_authenticate(request, user=user)
            view = YouTubeContentViewSet.as_view({'delete': 'destroy'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)


class CurveAPITestCase(APITestCase):
    def test_get_api(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 200],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            request = api.get('/api/curves/', format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'get': 'list'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_exist_both(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.create()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['content'] = data['content_id']
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_post_curve_with_exist_both_and_youtube(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.create()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['content'] = data['content_id']
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_not_exist_content(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.build()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            data['content'] = convert_to_dict_from(content)
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_post_curve_with_not_exist_youtube_content(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.build(video_id=randomname())
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            data['content'] = convert_to_dict_from(content)
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_exist_youtube_content(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.create(video_id=randomname())
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            data['content'] = convert_to_dict_from(content)
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_exist_content(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.create()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            data['content'] = convert_to_dict_from(content)
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_not_exist_value_type(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.create()
            value_type = ValueTypeFactory.build()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['value_type'] = convert_to_dict_from(value_type)
            data['content'] = data['content_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_not_exist_value_type(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.build()
            value_type = ValueTypeFactory.build()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['value_type'] = convert_to_dict_from(value_type)
            data['content'] = convert_to_dict_from(content)
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)
    
    def test_post_curve_with_not_exist_value_type(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.build()
            value_type = ValueTypeFactory.build()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['value_type'] = convert_to_dict_from(value_type)
            data['content'] = convert_to_dict_from(content)
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_post_curve_with_exist_youtube_content_but_has_not_id(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.create(video_id=randomname())
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.build(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            content_json = convert_to_dict_from(content)
            content_json["id"] = None
            data['content'] = content_json
            data['value_type'] = data['value_type_id']
            request = api.post('/api/curves/', data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'post': 'create'})
            response = view(request)
            self.assertEqual(response.status_code, status)

    def test_put_curve_with_exist_both(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.create()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.create(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['content'] = data['content_id']
            data['value_type'] = data['value_type_id']
            request = api.put("/api/curves/{obj.id}/", data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)

    def test_put_curve_with_exist_both_and_youtube(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.create()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.create(user=user, 
                content=content, value_type=value_type, room_name=randomname())

            data = convert_to_dict_from(obj)
            data['content'] = data['content_id']
            data['value_type'] = data['value_type_id']
            request = api.put("/api/curves/{obj.id}/", data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)
    
    def test_put_curve_with_exist_youtube_content(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.create(video_id=randomname())
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.create(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            data['content'] = convert_to_dict_from(content)
            data['value_type'] = data['value_type_id']
            request = api.put("/api/curves/{obj.id}/", data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)
    
    def test_put_curve_with_exist_content(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = ContentFactory.create()
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.create(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            data['content'] = convert_to_dict_from(content)
            data['value_type'] = data['value_type_id']
            request = api.put("/api/curves/{obj.id}/", data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)

    def test_put_curve_with_exist_youtube_content_but_has_not_id(self):
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            api = APIRequestFactory()
            user = User.objects.get(username=username)
            content = YouTubeContentFactory.create(video_id=randomname())
            value_type = ValueTypeFactory.create()
            obj = CurveFactory.create(user=user, 
                content=content, value_type=value_type, room_name=randomname())
            data = convert_to_dict_from(obj)
            content_json = convert_to_dict_from(content)
            content_json["id"] = None
            data['content'] = content_json
            data['value_type'] = data['value_type_id']
            request = api.put("/api/curves/{obj.id}/", data, format='json')
            force_authenticate(request, user=user)
            view = CurveViewSet.as_view({'put': 'update'})
            response = view(request, pk=obj.id)
            self.assertEqual(response.status_code, status)

class YouTubeContentAPITestCase(APITestCase):
    def test_get_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 200],
            ['general', 'password', 200],['researcher', 'password', 200]]:
            client.login(username=username, password=password)
            url = '/api/youtube/'
            response = client.get(url)
            self.assertEqual(response.status_code, status)
    
    def test_post_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 201], ['guest', 'password', 201],
            ['general', 'password', 201],['researcher', 'password', 201]]:
            client.login(username=username, password=password)
            url = '/api/youtube/'
            response = client.post(url, json.dumps({
                "title": Faker().word(),
                "url": Faker().url(),
                "video_id": randomname(),
                "channel_title": Faker().word(),
                "user": EmailUser.objects.get(username=username).id
            }), content_type="application/json")
            self.assertEqual(response.status_code, status)
    
    def test_put_api(self):
        client = APIClient()
        video_id = Faker().word()
        content = YouTubeContent.objects.create(
            title=Faker().word(),
            url=Faker().url(),
            video_id=video_id,
            channel_title=Faker().word(),
            user=EmailUser.objects.get(username='tomoya')
        )
        content.save()
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            client.login(username=username, password=password)
            url = '/api/youtube/' + str(content.id) + '/'
            response = client.put(url, json.dumps({
                "id": content.id,
                "title": Faker().word(),
                "url": Faker().url(),
                "video_id": video_id,
                "channel_title": Faker().word(),
                "user": EmailUser.objects.get(username=username).id
            }), content_type="application/json")
            self.assertEqual(response.status_code, status)

    def test_delete_api(self):
        client = APIClient()
        for username, password, status in [
            ['tomoya', 'youluck123', 200], ['guest', 'password', 403],
            ['general', 'password', 403],['researcher', 'password', 200]]:
            content = YouTubeContent.objects.create(
                title=Faker().word(),
                url=Faker().url(),
                video_id=Faker().word(),
                channel_title=Faker().word(),
                user=EmailUser.objects.get(username='tomoya')
            )
            content.save()
            client.login(username=username, password=password)
            url = '/api/youtube/' + str(content.id) + '/'
            response = client.delete(url)
            self.assertEqual(response.status_code, status)


class RequestAPITestCase(APITestCase):
    def test_api_superuser(self):
        client = APIClient()
        client.login(username='tomoya', password='youluck123')
        url = '/api/requests/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.put(url + "103/", json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)

        response = client.put(url + "103/", json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)

        response = client.put(url + "103/", json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="tomoya").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
    
    def test_api_generaluser(self):
        client = APIClient()
        client.login(username='general', password='password')
        url = '/api/requests/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="general").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 403)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="general").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 403)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username="general").id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 403)
    

    def test_api_researcher(self):
        USERNAME = "researcher"
        client = APIClient()
        client.login(username=USERNAME, password='password')
        url = '/api/requests/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username=USERNAME).id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                EmailUserFactory.create().email
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username=USERNAME).id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                Faker().email(),
                Faker().email(),
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = client.post(url, json.dumps({
            "title": Faker().word(),
            "description": Faker().sentence(),
            "intervals": random.randint(1, 20),
            "owner": EmailUser.objects.get(username=USERNAME).id,
            "content": 1,
            "value_type": 1,
            "questionaire": "",
            "participants": [
                EmailUserFactory.create().email,
                EmailUserFactory.create().email,
                Faker().email(),
            ]
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
