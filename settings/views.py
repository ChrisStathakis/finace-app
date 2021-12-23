from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from .models import UserDateRange, ProfileSetting
from .forms import UserDateRangeForm


@login_required
def homepage_view(request):
    user, context = request.user, dict()
    settings = ProfileSetting.objects.get_or_create(user=user)
    date_ranges = UserDateRange.objects.filter(settings__user=user)
    context['date_ranges'] = date_ranges
    date_range_form = UserDateRangeForm(request.POST or None, initial={'settings': settings})
    if date_range_form.is_valid():
        date_range_form.save()
        return redirect(reverse('setting:homepage'))
    else:
        print(date_range_form.errors)
    context['date_range_form'] = date_range_form

    return render(request, 'settings/homepage.html', context=context)



