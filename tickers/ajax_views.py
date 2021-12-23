from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, reverse, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import Ticker, Portfolio
from .form import UserTickerForm

import pandas as pd
import numpy as np
from decimal import Decimal

from random import randint
from .get_stock_data import read_data, get_stock_data


@login_required
def search_tickers(request, pk):
    instance = get_object_or_404(Portfolio, id=pk)
    data = dict()
    tickers = Ticker.filter_data(request)
    data['result'] = render_to_string(template_name='ajax/tickers_table.html',
                                       request=request,
                                       context={
                                           'tickers': tickers,
                                           'instance': instance
                                       }
                                       )
    return JsonResponse(data)


@login_required
def ajax_add_ticker_modal(request, pk, dk):
    instance = get_object_or_404(Portfolio, id=pk, user=request.user)
    ticker = get_object_or_404(Ticker, id=dk)
    form = UserTickerForm(request.POST or None, initial={'ticker': ticker,
                                                         'portfolio': instance,
                                                         'starting_value_of_ticker': round(ticker.price, 8)
                                                         }
                          )

    data = dict()
    data['result'] = render_to_string(template_name='ajax/ticker_edit_modal.html',
                                      request=request,
                                      context={
                                          'title': 'New Ticker',
                                          'form': form,
                                          'success_url': reverse('portfolio:validate_create_ticker_from_portfolio',
                                                                 kwargs={'pk': instance.id, 'dk': ticker.id})

                                      }
                                      )
    return JsonResponse(data)


@login_required
def ajax_portfolio_effective_frontier_view(request, pk):
    instance = get_object_or_404(Portfolio, id=pk)
    effective_frontier = instance.effecient_frontier()
    weight_analysis = []
    weights, expected_returns, expected_volatility, total_money = effective_frontier[0], effective_frontier[1], effective_frontier[2], effective_frontier[3]
    for i in range(len(weights)):
        new_list = [weights[i], f'{round(expected_returns[i]*100, 2)} %', f'{round(expected_volatility[i]*100, 2)} %', total_money[i]]
        weight_analysis.append(new_list)

    data = dict()
    data['result'] = render_to_string(template_name='tickers/ajax/effective_frontier.html',
                                      request=request,
                                      context={
                                          'instance': instance,
                                          'weights': weights,
                                          'expected_return': expected_returns,
                                          'expected_volatility': expected_volatility,
                                          'weight_analysis': weight_analysis

                                      }
                                      )
    return JsonResponse(data)


@login_required
def ajax_show_historic_graph(request, pk):
    instance = get_object_or_404(Ticker, id=pk)
    context, data = dict(), dict()
    historic_data = instance.get_ticker_data()
    context['historic_data'] = historic_data
    context['historic_graph'] = instance.show_graph(historic_data)
    data['result'] = render_to_string(template_name='tickers/ajax/graph_card.html',
                                      request=request,
                                      context=context)
    return JsonResponse(data)


@login_required
def create_random_portfolios_view(request, pk):
    obj = get_object_or_404(Portfolio, id=pk)
    tickers_max = int(request.GET.get('max', 2))
    iterations = int(request.GET.get('iter', 10))
    count = Ticker.objects.count()
    combinations = []
    for i in range(int(iterations)):
        tickers_list = []
        random_index_choices = []
        while len(tickers_list) < tickers_max:
            random_index = randint(0, count - 1)
            choice = Ticker.objects.all()[random_index]
            if random_index not in random_index_choices:
                random_index_choices.append(random_index)
                tickers_list.append(choice)
        combinations.append(tickers_list)
    calculate_combinations = []
    for tickers in combinations:
        try:
            weights = []
            assets = [tic.ticker for tic in tickers]
            df_data = pd.DataFrame()
            for a in assets:
                weights.append(1/len(tickers))
                get_stock_data(a)
                df = read_data(a)
                df_data = df if df_data.empty else df_data.join(df, how='outer')
            weights = np.array(weights)
            log_returns = np.log(df_data / df_data.shift(1))
            mean = log_returns.mean()
            expected_portofolio_return = round(Decimal(np.sum(weights * mean)) * 250,4)
            expected_portfolio_variance = round(np.dot(weights.T, np.dot(log_returns.cov() * 250, weights)), 4)
            expected_portfolio_volatility = round(np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 250, weights))), 4)
            new_list = [tickers, expected_portofolio_return, expected_portfolio_variance, expected_portfolio_volatility]
            calculate_combinations.append(new_list)
        except:
            continue

    data = dict()

    data['result'] = render_to_string(template_name='ajax/add_random_tickers.html',
                                      request=request,
                                      context={
                                          'table_list': calculate_combinations,
                                          'instance': obj
                                      }
                                      )
    return JsonResponse(data)


@login_required
def ajax_ticker_modal(request, pk, dk):
    portfolio = get_object_or_404(Portfolio, id=pk)
    ticker = get_object_or_404(Ticker, id=dk)
    data = dict()
    data['result'] = render_to_string(template_name='tickers/ajax/ajax_modal_ticker_show.html',
                                      request=request,
                                      context={
                                          'ticker': ticker,
                                          'instance': portfolio
                                      }
                                      )
    return JsonResponse(data)


@login_required
def ajax_refresh_portfolio_data(request, pk):
    portfolio = get_object_or_404(Portfolio, id=pk)
    for ticker in portfolio.tickers.all():
        print('yrh')
        ticker.update_ticker_data()
    data = dict()
    data['result'] = render_to_string(template_name='ajax/portfolio_tickers_table.html',
                                      request=request,
                                      context={
                                          'instance': portfolio

                                      }
                                      )
    data['port_stats'] = render_to_string(
        template_name='ajax/port_stats.html',
        request=request,
        context={
            'instance': portfolio
        }
    )
    return JsonResponse(data)