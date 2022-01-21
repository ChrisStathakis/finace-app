from django.shortcuts import get_object_or_404, redirect, HttpResponseRedirect, render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

import numpy as np
import pandas as pd
import datetime
from random import randint

from .models import Ticker, Portfolio, UserTicker, User

from .form import UserTickerForm, TickerRefreshForm
from .get_stock_data import read_data, get_stock_data


@login_required
def refresh_portfolio_action_view(request, pk):
    portfolio = get_object_or_404(Portfolio, id=pk, user=request.user)
    tickers = portfolio.tickers.all()

    for user_ticker in tickers:
        if user_ticker.is_sell:
            continue
        else:
            user_ticker.update_ticker_data()
    return HttpResponseRedirect(portfolio.get_absolute_url())


@login_required
def delete_portfolio_view(request, pk):
    obj = get_object_or_404(Portfolio, id=pk)
    obj.delete()
    return redirect(reverse('portfolio:portfolio_list_view'))


@login_required
def refresh_tickers_data(request):
    tickers = Ticker.objects.all()
    for instance in tickers:
        get_stock_data(instance.ticker)
        instance.update_ticker_data()

    return redirect(reverse('portfolio:ticker_list_view'))


@login_required
def refresh_ticker_data(request, pk):
    instance = get_object_or_404(Ticker, id=pk)
    instance.update_ticker_data()
    return redirect(instance.get_absolute_url())


@login_required
def update_ticker_api_view(request, pk, slug):
    print('jherefdsf d')
    ticker = get_object_or_404(Ticker, id=pk)
    ticker.save()

    # moved the updated method to save method, so api viewa uodate too
    return redirect(ticker.get_absolute_url())


@login_required
def validate_ticker_create_from_portfolio_view(request, pk, dk):
    instance = get_object_or_404(Portfolio, id=pk, user=request.user)
    ticker = get_object_or_404(Ticker, id=dk)
    get_stock_data(ticker.group.code if ticker.group else '^GSPC')
    ticker.update_ticker_data()
    form = UserTickerForm(request.POST or None, initial={'ticker': ticker, 'portfolio': instance})
    if form.is_valid():
        ticker = form.save()
    else:
        print(form.errors)
    return redirect(instance.get_absolute_url())


@login_required
def buy_tickers_from_effective_frontier_view(request, pk):
    instance = get_object_or_404(Portfolio, id=pk)
    instance.add_tickers_to_portfolio(request)
    return redirect(instance.get_absolute_url())


@login_required
def delete_ticker_from_portfolio_view(request, pk):
    obj = get_object_or_404(UserTicker, id=pk, portfolio__user=request.user)
    obj.delete()
    return redirect(obj.portfolio.get_absolute_url())


@login_required
def update_user_ticker_view(request, pk):
    obj = get_object_or_404(UserTicker, id=pk, portfolio__user=request.user)
    form = UserTickerForm(request.POST or None, instance=obj)

    if form.is_valid():
        ticker = form.save()
        if ticker.is_buy:
            ticker.update_data_on_buy()

        return redirect(obj.portfolio.get_absolute_url())
    page_title, back_url = f'Edit {obj}', obj.portfolio.get_absolute_url()
    return render(request, 'form_view.html', context={'form': form,
                                                      'page_title': page_title,
                                                      'back_url': back_url,
                                                      })


@login_required
def add_random_tickers_to_portfolio(request, pk):
    obj = get_object_or_404(Portfolio, id=pk)
    ids = request.GET.get('tickers', None)
    ids = ids.replace(' ', '')

    if ids:
        ids = ids.split(',')
        tickers = Ticker.objects.filter(id__in=ids)
        for ticker in tickers:
            UserTicker.objects.create(
                ticker=ticker,
                portfolio=obj
            )

    return redirect(obj.get_absolute_url())




