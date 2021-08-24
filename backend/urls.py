from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from .settings.devl import STATIC_URL, STATIC_ROOT
from .views import app, index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('users.urls')),
    url(r'^history/', include('users.history')),
    url(r'^app/', app, name='app'),
    url(r'^auth/', include('django.contrib.auth.urls')),
    url('^$', index, name='index'),
] + static(STATIC_URL, document_root=STATIC_ROOT)
