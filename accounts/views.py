from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .forms import CustomUserCreationForm


def register(request):
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(reverse('homepage'))
    return render(request, 'login.html', {'form': form,
                                          'page_title': 'Register',
                                          'url_change': reverse('login'),
                                          'btn_name': 'Login'
                                          })


@login_required
def profile_view(request):
    context, user = dict(), request.user
    context['portfolios'] = user.portfolios.all()

    return render(request, 'profile.html', context)
