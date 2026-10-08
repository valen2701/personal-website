from django.contrib.auth import authenticate, get_user_model, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse


def index(request):
    return render(request, "portfolio/index.html", {})


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('portfolio:index')
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None and username and not get_user_model().objects.filter(username=username).exists():
            user = get_user_model().objects.create_user(username=username, password=password)
            user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect(next_url)

    return render(request, 'registration/login.html', {'form': form, 'next': next_url})
