from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'curves', CurveViewSet)
router.register(r'contents', ContentViewSet)
router.register(r'valuetypes', ValueTypeViewSet)
urlpatterns = router.urls
