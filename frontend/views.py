from django.shortcuts import render, HttpResponseRedirect, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db.models import Sum, F, Avg

import pandas as pd
import datetime
from dateutil import relativedelta


from tickers.models import Portfolio
from tickers.models import Ticker
from strategies.models import Strategy, StrategyTicker
from .forms import LoginForm
from tickers.form import PortFolioForm


@login_required
def homepage(request):
    context = dict()
    portfolios = Portfolio.objects.filter(user=request.user)
    context['portfolios'] = portfolios
    form = PortFolioForm(request.POST or None, initial={'user': request.user})
    if form.is_valid():
        form.save()
    context['form'] = form
    context['count_portfolios'] = portfolios.count()
    context['total_earnings'] = total_earnings = round(portfolios.aggregate(total=Sum(F('current_value')-F('starting_investment'))) if portfolios.exists() else 0,2)
    context['average_earnings'] = total_earnings['total']/portfolios.count() if portfolios.exists() else 0
    context['starting_investment'] = portfolios.aggregate(Sum('starting_investment'))['starting_investment__sum'] if portfolios.exists() else 0
    context['average_expected_earnings'] = portfolios.aggregate(Avg('expected_portfolio_return'))['expected_portfolio_return__avg'] if portfolios.exists() else 0
    context['average_expected_variance'] = portfolios.aggregate(Avg('expected_portfolio_variance'))[
        'expected_portfolio_variance__avg'] if portfolios.exists() else 0
    return render(request, 'dashboard.html', context)


def login_view(request):
    page_title = 'login'
    user = request.user
    url_change, btn_name = reverse('accounts:register'), 'Register'
    if user.is_authenticated:
        return HttpResponseRedirect('/')
    login_ = True
    form = LoginForm(request.POST or None)
    form_title, form_button = 'Συνδεση', 'Συνδεση'
    text = 'Εάν έχετε ήδη λογαριασμό, μπορείτε να συνδεθείτε'
    if form.is_valid():
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=raw_password)
        if user:
            login(request, user)
            return redirect('homepage')
        else:
            messages.warning(request, 'Ο κωδικός ή το email είναι λάθος.')
    return render(request, 'login.html', context=locals())


class StrategyView(TemplateView):
    template_name = 'strategy_homepage_view.html'


@login_required
def moving_average_trading_strategy_view(request):
    context = dict()
    context['object_list'] = Ticker.objects.all()[:50]
    strategy = Strategy.objects.get_or_create(user=request.user, category='a')
    context['strategy'] = strategy[0]
    strategy_tickers = StrategyTicker.objects.filter(strategy=strategy[0])
    context['strategy_tickers'] = strategy_tickers
    chart_data = pd.DataFrame()
    date = datetime.datetime.now() - relativedelta.relativedelta(month=3)

    data = dict()
    for ticker in strategy_tickers:
        MACD_line, signal_line, histogram = ticker.MACD()
        MACD_line = ['MACD', [MACD_line.columns.tolist() + MACD_line.reset_index().values.tolist()]]
        signal_line = ['Signal line', [signal_line.columns.tolist() + signal_line.reset_index().values.tolist()]]
        histogram = ['histogram', [histogram.columns.tolist() + histogram.reset_index().values.tolist()]]
        data[ticker.ticker.ticker] = [MACD_line, signal_line, histogram]
        # ticker.generate_signal(ticker.get_dataframe())
    context['data'] = data

    for ticker in strategy_tickers:
        ticker = ticker.ticker
        df = ticker.moving_average_trading_strategy(start_date=date)
        chart_data = df if chart_data.empty else chart_data.join(df, how='outer')
    chart_data.dropna(inplace=True)
    chart_headers = list(chart_data.columns.tolist())
    chart_data = [chart_data.columns.tolist()] + chart_data.reset_index().values.tolist()
    StrategyTicker.calculate_historic_rsi([ticker.ticker.ticker for ticker in strategy_tickers])
    context['chart_data'] = chart_data
    context['chart_headers'] = chart_headers
    context['portfolios'] = Portfolio.objects.filter(user=request.user)
    return render(request, 'tickers/moving_average_trading_view.html', context=context)


@login_required
def add_ticker_to_strategy_view(request, pk, dk):
    strategy = get_object_or_404(Strategy, id=pk)
    ticker = get_object_or_404(Ticker, id=dk)
    new_strategy_ticker = StrategyTicker.objects.create(
        strategy=strategy,
        ticker=ticker
    )
    messages.success(request, f'New ticker added - {new_strategy_ticker}')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def delete_ticker_from_strategy_view(request, pk):
    ticker = get_object_or_404(StrategyTicker, id=pk)
    ticker.delete()
    messages.warning(request, f'Ticker {ticker} removed from the strategy')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
