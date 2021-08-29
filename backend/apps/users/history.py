from rest_framework.routers import DefaultRouter
from .views import ContentHistoryViewSet, ValueTypeHistoryViewSet, CurveHistoryViewSet

router = DefaultRouter()
router.register(r'contents', ContentHistoryViewSet, base_name='history/contents')
router.register(r'valuetypes', ValueTypeHistoryViewSet, base_name='history/valuetypes')
router.register(r'curves', CurveHistoryViewSet, base_name='history/curves')
urlpatterns = router.urls
