from django.conf.urls import url, include
from django.contrib.auth import views as auth
from django.urls import reverse_lazy

from .views import *

urlpatterns = [
    url(r'login', auth.LoginView.as_view(), name='login'),
    url(r'logout', auth.LogoutView.as_view(), { 'next_page': reverse_lazy('index') }, name='logout'),
    url(r'signup', signup, name='signup')
]
