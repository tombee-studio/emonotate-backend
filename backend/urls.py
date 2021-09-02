import os
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from .settings.common import STATIC_URL, BASE_DIR
from .views import app, index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('users.urls')),
    url(r'^history/', include('users.history')),
    url(r'^app/', app, name='app'),
    url(r'^auth/', include('auth.urls')),
    url('^$', index, name='index'),
]

if os.environ['STAGE'] == 'DEVL':
    urlpatterns += static(STATIC_URL)
elif os.environ['STAGE'] == 'ALPHA':
    urlpatterns += static(STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))
elif os.environ['STAGE'] == 'PROD':
    from .settings.prod import STATIC_ROOT
    urlpatterns += static(STATIC_URL, STATIC_ROOT)
