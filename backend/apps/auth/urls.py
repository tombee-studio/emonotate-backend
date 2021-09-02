from django.conf.urls import url, include
from django.contrib.auth import views as auth
from django.core.urlresolvers import reverse_lazy

from .views import *

urlpatterns = [
    url(r'login', auth.login, name='login'),
    url(r'logout', auth.logout, { 'next_page': reverse_lazy('index') }, name='logout'),
    url(r'signup', signup, name='signup')
]
