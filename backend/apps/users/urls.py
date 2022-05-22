from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from .views import *

from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'curves', CurveViewSet, basename='curves')
router.register(r'contents', ContentViewSet, basename='contents')
router.register(r'youtube', YouTubeContentViewSet, basename='youtube')
router.register(r'valuetypes', ValueTypeViewSet, basename='valuetypes')
router.register(r'requests', RequestViewSet, basename='requests')
router.register(r'curves_with_youtube', CurveWithYouTubeContentViewSet, basename='curve_with_youtube')
urlpatterns = router.urls
urlpatterns += url(r'sign_s3/$', sign_s3),
urlpatterns += path('me/', Me.as_view(), name='login'),
urlpatterns += path('login/', LoginAPIView.as_view(), name='login'),
urlpatterns += path('logout/', LogoutAPIView.as_view(), name='logout'),
