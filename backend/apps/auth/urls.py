from django.conf.urls import url, include
from django.contrib.auth import views as auth
from django.urls import reverse_lazy, path

from .views import *

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    url(r'signup', signup, name='signup')
]
