from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from .views import *

from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication

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
urlpatterns += path('signup/', SignupAPIView.as_view(), name='signup'),
urlpatterns += path('send/<int:pk>', send_request_mail),
urlpatterns += path('get_download_curve_data/<int:pk>', get_download_curve_data),
urlpatterns += path('download_curve_data/', download_curve_data),
urlpatterns += path('reset_email_addresses/<int:pk>', reset_email_addresses),
