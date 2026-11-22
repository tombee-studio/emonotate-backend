import os
import json

from importlib import import_module

from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import urlencode
from django.views.generic import View

User = get_user_model()

def index(request):
    content = ""
    #--------
    # * APIとして利用する際には上側を使用
    #--------
    # return JsonResponse(UserSerializer(request.user).data, status=200)

    #--------
    # frontend として使用する際には下側を使用
    #--------
    # ROOT_DOMAIN = "herokuapp.com" if os.environ.get("STAGE") == "alpha" else "emonotate.com"
    module = import_module(os.environ.get('DJANGO_SETTINGS_MODULE'))
    queries = [f'{query}={request.GET[query]}' for query in request.GET]
    if not request.user.is_authenticated:
        return redirect(f"{module.APPLICATION_URL}app/login/{'' if not request.GET else '?' + '&'.join(queries)}")
    return redirect(module.APPLICATION_URL)


@login_required
def app(request):
    context = {
        'permissions': json.dumps(list(request.user.get_all_permissions())),
        'YOUTUBE_API_KEY': os.environ.get('YOUTUBE_API_KEY')
    }

    template = 'backend/app.html'
    return render(request, template, context)


class InputScreenView(View):
    """The old input screens moved to the app; saved links still lead to them."""
    kind = None

    def get(self, request, pk=None):
        if pk:
            return redirect(f"/app/curves/{pk}/")
        if "request" in request.GET:
            return redirect("/app/curves/?" + urlencode({"request": request.GET["request"]}))
        if "video_id" in request.GET:
            return redirect("/app/curves/?" + urlencode({"videoId": request.GET["video_id"], "kind": self.kind}))
        return redirect("/app/dashboard/")
