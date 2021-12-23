from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from tickers.models import Ticker, User, Portfolio, UserTicker
from .models import BackupSignature
from .admin import UserResources, TickerResources, PortfolioResources, UserTickerResources

from .models import BackupSignature


@method_decorator(staff_member_required, name='dispatch')
class BackupHomepageView(TemplateView):
    template_name = 'backupFolder/backupDatabase.html'

    def get_context_data(self, **kwargs):
        context = super(BackupHomepageView, self).get_context_data(**kwargs)
        # Ticker
        context['count_ticker'] = Ticker.objects.count()
        context['last_ticker'] = BackupSignature.objects.filter(title='ticker').last().timestamp if BackupSignature.objects.filter(title='ticker').exists() else 'No backup'
        # User
        context['count_user'] = User.objects.count()
        context['last_user'] = BackupSignature.objects.filter(title='ticker').last().timestamp if BackupSignature.objects.filter(title='user').exists() else 'No backup'
        # portfolio
        context['count_portfolio'] = Portfolio.objects.count()
        context['last_portfolio'] = BackupSignature.objects.filter(title='ticker').last().timestamp if BackupSignature.objects.filter(title='portfolio').exists() else 'No backup'
        # UserTicker
        context['count_user_ticker'] = UserTicker.objects.count()
        context['last_user_ticker'] = BackupSignature.objects.filter(title='ticker').last().timestamp if BackupSignature.objects.filter(title='user_ticker').exists() else 'No backup'
        return context


@staff_member_required
def download_data_view(request, slug):
    print('hittes!')
    key_list = ['user', 'portfolio', 'user_ticker', 'ticker']
    resources = {
        'user': UserResources,
        'portfolio': PortfolioResources,
        'user_ticker': UserTickerResources,
        'ticker': TickerResources
    }
    key_exists = True if slug in key_list else False
    if not key_exists:
        print('not here')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    resource = resources[slug]
    dataset = resource().export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{slug}.csv"'
    BackupSignature.objects.create(title=slug)
    return response
