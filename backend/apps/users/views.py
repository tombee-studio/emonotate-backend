from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .models import ValueType, Curve, Content

from .serializers import UserSerializer
from .serializers import ValueTypeSerializer, ContentSerializer, CurveSerializer


User = get_user_model()


class ValueTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ValueTypeSerializer
    queryset = ValueType.objects.all()
    search_fields = 'id'


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()
    search_fields = 'id'


class CurveViewSet(viewsets.ModelViewSet):
    serializer_class = CurveSerializer
    queryset = Curve.objects.all()
    search_fields = 'id'


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    search_fields = ('username', 'email')
    filter_fields = ('id', 'username', 'email')
