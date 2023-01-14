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
router.register(r'enquetes', EnqueteViewSet, basename='enquetes')
router.register(r'requests', RequestViewSet, basename='requests')
router.register(r'sections', SectionViewSet, basename='sections')
router.register(r'google_forms', GoogleFormViewSet, basename='sections')
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
urlpatterns += path('change_email/', change_email),
urlpatterns += path('merge_accounts/', merge_accounts),
urlpatterns += path('participants/<int:pk>', ParticipantView.as_view(), name="participants"),
urlpatterns += path('inviting_tokens/', InvitingTokenView.as_view(), name='inviting_tokens'),
urlpatterns += path('relative_users/', RelativeUsersView.as_view(), name='relative_users'),
urlpatterns += path('verify/', UserVerifyView.as_view(), name='verify'),
