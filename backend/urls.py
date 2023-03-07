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
    path('free-hand/', FreeHandView.as_view(), name='free-hand'),
    path('free-hand/<int:pk>', FreeHandDetailView.as_view(), name='free-hand-detail'),
    path('fold-line/', FoldLineView.as_view(), name='fold-line'),
    path('fold-line/<int:pk>', FoldLineDetailView.as_view(), name='free-hand'),
    url(r'^auth/', include('auth.urls')),
    url('^$', index, name='index'),
]

if os.environ['STAGE'] == 'DEVL':
    urlpatterns += static(STATIC_URL)
elif os.environ['STAGE'] == 'ALPHA':
    urlpatterns += static(STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))
elif os.environ['STAGE'] == 'PROD':
    urlpatterns += static(STATIC_URL)
