from rest_framework.routers import DefaultRouter
from django.conf.urls import url
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'curves', CurveViewSet)
router.register(r'contents', ContentViewSet)
router.register(r'history_contents', ContentHistoryViewSet)
router.register(r'valuetypes', ValueTypeViewSet)
urlpatterns = router.urls
urlpatterns += url(r'sign_s3/$', sign_s3),
