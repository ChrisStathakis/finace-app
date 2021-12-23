from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from strategies.models import Strategy, StrategyTicker
from tickers.models import Portfolio


@login_required
def add_portfolio_to_strategy_view(request, pk, dk):
    strategy = get_object_or_404(Strategy, id=pk)
    for ticker in strategy.my_tickers.all():
        ticker.delete()
    portfolio = get_object_or_404(Portfolio, id=dk)
    for ticker in portfolio.tickers.all():
        StrategyTicker.objects.create(
            ticker=ticker.ticker,
            strategy=strategy
        )
    return redirect(request.META.get('HTTP_REFERER'))



