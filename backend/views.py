import os
import json

from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect

from lazysignup.decorators import allow_lazy_user

from django.http import JsonResponse

User = get_user_model()

@allow_lazy_user
def index(request):
    content = ""
    return JsonResponse({
        "user": {
            "user_id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        },
        "message": "Hello, World!"
    }, status=200)


@login_required
def app(request):
    context = {
        'permissions': json.dumps(list(request.user.get_all_permissions())),
        'YOUTUBE_API_KEY': os.environ.get('YOUTUBE_API_KEY')
    }

    template = 'backend/app.html'
    return render(request, template, context)
