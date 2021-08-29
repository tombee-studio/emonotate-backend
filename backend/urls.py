import os
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from .settings.devl import STATIC_URL, DEBUG
from .views import app, index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('users.urls')),
    url(r'^history/', include('users.history')),
    url(r'^app/', app, name='app'),
    url(r'^auth/', include('auth.urls')),
    url('^$', index, name='index'),
]

if DEBUG:
    urlpatterns += static(STATIC_URL)
else:
    from .settings.prod import STATIC_ROOT
    urlpatterns += static(STATIC_URL, STATIC_ROOT)
