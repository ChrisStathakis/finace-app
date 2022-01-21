from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from .models import Portfolio, Ticker, Group
from .form import UserTickerForm, TickerForm, GroupForm, PortFolioForm


from .get_stock_data import read_data, check_if_file_exists
import pandas as pd
from scipy.stats import norm


def portofolio_view(request, id):
    context = dict()
    instance = get_object_or_404(Portfolio, id=id)
    instance.calculate_returns_and_volatility()
    portForm = PortFolioForm(request.POST or None, instance=instance)
    if portForm.is_valid():
        portForm.save()
        return redirect(instance.get_absolute_url())
    context['instance'] = instance
    create_form = UserTickerForm(request.POST or None, initial={'portfolio': instance})
    context['create_form'] = create_form
    context['ticker_form'] = TickerForm()
    context['portForm'] = portForm
    if create_form.is_valid():
        create_form.save()
        return redirect(instance.get_absolute_url())
    ids = []
    forecast_data = []
    for tic in instance.tickers.all():
        ids.append(tic.ticker.id)
        forecast_data.append([tic, tic.ticker.forecast()])
    context['forecast_data'] = forecast_data
    context['tickers'] = Ticker.objects.all()[:100]
    return render(request, 'portfolio.html', context)


class TickerListView(ListView):
    model = Ticker
    paginate_by = 20
    template_name = 'ticker_list_view.html'
    queryset = Ticker.objects.all()

    def get_queryset(self):
        return Ticker.filter_data(self.request)

    def get_context_data(self, **kwargs):
        context = super(TickerListView, self).get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['ticker_form'] = TickerForm()
        context['group_form'] = GroupForm()

        return context


@method_decorator(login_required, name='dispatch')
class TickerUpdateView(UpdateView):
    template_name = 'tickers/update_view.html'
    model = Ticker
    form_class = TickerForm
    success_url = reverse_lazy('portfolio:ticker_list_view')
    queryset = Ticker.objects.all()

    def get_context_data(self, **kwargs):
        context = super(TickerUpdateView, self).get_context_data(**kwargs)
        file_exists = check_if_file_exists(self.object.ticker)

        if file_exists:
            print('file exists')
            context['macd'], context['safe_line'], context['tick'] = self.object.calculate_macd()
            df_sma = self.object.bb()
            df_sma.dropna(inplace=True)
            df_sma = [df_sma.columns.tolist()] + df_sma.reset_index().values.tolist()

            df = self.object.create_data_for_chart()
            df = [df.columns.tolist()] + df.reset_index().values.tolist()
            new_list, new_sma_list = [], []
            for ele in df:
                if self.object.ticker in ele:
                    continue
                else:
                    new_list.append(ele)
            for ele in df_sma:
                new_sma_list.append(ele) if self.object.ticker in ele else ''

            context['df_sma'] = df_sma
            context['chart_data'] = new_list
            context['delete_url'] = self.object.get_delete_url()
            context['graph'] = self.object.monte_carlo_simulation()
            context['ticker_avg'] = self.object.calculate_averages()
            context['drop_5_prop'] = self.object.calculate_probability_of_drop(0.05)
            context['gain_5_prop'] = self.object.calculate_probability_of_drop(-0.05)

        else:
            messages.warning(self.request, f'Code {self.object.ticker} dont exist on yahoo database')

        return context

    def form_valid(self, form):
        form.save()
        return super(TickerUpdateView, self).form_valid(form)


@login_required
def ticker_delete_view(request, id):
    ticker = get_object_or_404(Ticker, id=id, user=request.user)
    ticker.delete()
    return redirect('portfolio:ticker_list_view')


@method_decorator(login_required, name='dispatch')
class PortfoliosListView(ListView):
    template_name = 'portfolios_list_view.html'
    model = Portfolio
    paginate_by = 50

    def get_queryset(self):
        user = self.request.user
        return Portfolio.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super(PortfoliosListView, self).get_context_data(**kwargs)
        context['form'] = PortFolioForm(self.request.POST or None, initial={'user': self.request.user})

        return context


@login_required
def portfolio_delete_view(request, pk):
    obj = get_object_or_404(Portfolio, id=pk, user=request.user)
    obj.delete()
    return redirect(reverse('homepage'))


def calculate_relative_strength_index_view(request):
    tickers = Ticker.objects.all()[:10]
    for ticker in tickers:
        df = read_data(ticker.ticker)


