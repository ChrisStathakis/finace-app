from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .form import TickerForm, GroupForm, PortFolioForm

import datetime


@login_required
def validate_create_ticker_form(request):
    form = TickerForm(request.POST or None)
    if form.is_valid():
        ticker = form.save()
        ticker.update_ticker_data(request)
        ticker.updated = datetime.datetime.now()
        ticker.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def validate_create_group_form(request):
    form = GroupForm(request.POST or None)
    if form.is_valid():
        form.save()

    return redirect('portfolio:ticker_list_view')


@login_required
def validate_portfolio_create_form(request):
    form = PortFolioForm(request.POST or None, initial={'user': request.user})
    if form.is_valid():
        new_portfolio = form.save()
        return HttpResponseRedirect(new_portfolio.get_absolute_url())
    return redirect('portfolio:portfolio_list_view')
