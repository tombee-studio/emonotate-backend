from rest_framework.routers import DefaultRouter
from .views import ContentHistoryViewSet, ValueTypeHistoryViewSet, CurveHistoryViewSet

router = DefaultRouter()
router.register(r'contents', ContentHistoryViewSet)
router.register(r'valuetypes', ValueTypeHistoryViewSet)
router.register(r'curves', CurveHistoryViewSet)
urlpatterns = router.urls
