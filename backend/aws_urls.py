from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie

from backend import views
from users import cognito, sources
from users import views as users
from users.urls import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/passport/", cognito.passport),
    path("api/cognito/login/", cognito.start),
    path("api/cognito/callback/", cognito.callback),
    path("api/logout/", cognito.sign_out),
    path("api/me/", ensure_csrf_cookie(cognito.me)),
    path("api/sources/upload/", sources.upload),
    path("api/sources/", sources.register),
    path("api/sources/<int:pk>/file/", sources.file_url),
    path("api/", include(router.urls)),
    path("history/", include("users.history")),
    path("free-hand/", views.FreeHandView.as_view()),
    path("free-hand/<int:pk>", views.FreeHandDetailView.as_view()),
    path("fold-line/", views.FoldLineView.as_view()),
    path("fold-line/<int:pk>", views.FoldLineDetailView.as_view()),
    path("api/send/<int:pk>", users.send_request_mail),
    path("api/get_download_curve_data/<int:pk>", users.get_download_curve_data),
    path("api/download_curve_data/", users.download_curve_data),
    path("api/participants/<int:pk>", users.ParticipantView.as_view()),
    path("api/inviting_tokens/", users.InvitingTokenView.as_view()),
    path("api/relative_users/", users.RelativeUsersView.as_view()),
    path("api/set_section/<int:pk>", users.SetSectionView.as_view()),
    path("api/set_google_form/<int:pk>", users.SetGoogleFormView.as_view()),
]
