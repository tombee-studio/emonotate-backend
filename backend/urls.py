import os
from django.urls import path
from django.urls import re_path as url, include
from django.conf.urls.static import static
from django.contrib import admin

from .settings.common import STATIC_URL, BASE_DIR
from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('users.urls')),
    url(r'^history/', include('users.history')),
    path('free-hand/', InputScreenView.as_view(kind=1), name='free-hand'),
    path('free-hand/<int:pk>', InputScreenView.as_view(), name='free-hand-detail'),
    path('fold-line/', InputScreenView.as_view(kind=2), name='fold-line'),
    path('fold-line/<int:pk>', InputScreenView.as_view(), name='free-hand'),
    url(r'^auth/', include('auth.urls')),
    url('^$', index, name='index'),
]

_stage = os.environ.get('STAGE', '')
if _stage == 'DEVL':
    urlpatterns += static(STATIC_URL)
elif _stage == 'ALPHA':
    urlpatterns += static(STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))
elif _stage == 'PROD':
    urlpatterns += static(STATIC_URL)
