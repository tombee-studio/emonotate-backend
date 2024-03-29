from django.http import HttpResponse
from django.contrib.auth import login, authenticate, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Permission, Group

from .forms import SignUpForm

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = User.objects.create_user(username, email, raw_password)
            user.save()
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'ユーザー登録が完了しました！')
                return redirect('index')
            else:
                print('user is {}'.format(user))
                return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
