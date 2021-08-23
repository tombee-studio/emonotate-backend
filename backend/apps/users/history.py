from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'contents', ContentHistoryViewSet, base_name='hisotry/contents')
urlpatterns = router.urls
