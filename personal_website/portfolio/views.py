from django.contrib.auth import authenticate, get_user_model, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def index(request):
    return render(request, "portfolio/index.html", {})


def login_view(request):
    requested_next = request.POST.get('next') or request.GET.get('next')
    next_url = (
        requested_next
        if requested_next
        and url_has_allowed_host_and_scheme(
            requested_next,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
        else reverse('portfolio:index')
    )
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
