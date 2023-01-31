import os
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from .settings.common import STATIC_URL, BASE_DIR
from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('users.urls')),
    url(r'^history/', include('users.history')),
    path('free-hand/', free_hand_view, name='free-hand'),
    path('fold-line/', fold_line_view, name='fold-line'),
    url(r'^auth/', include('auth.urls')),
    url(r'^convert/', include('lazysignup.urls')),
    url('^$', index, name='index'),
]

if os.environ['STAGE'] == 'DEVL':
    urlpatterns += static(STATIC_URL)
elif os.environ['STAGE'] == 'ALPHA':
    urlpatterns += static(STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))
elif os.environ['STAGE'] == 'PROD':
    from .settings.prod import STATIC_ROOT
    urlpatterns += static(STATIC_URL, STATIC_ROOT)
