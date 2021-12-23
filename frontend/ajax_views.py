from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string

from tickers.models import Portfolio
from strategies.models import Strategy


@login_required
def ajax_show_portfolios_view(request, pk):

    strategy = get_object_or_404(Strategy, id=pk)
    user = request.user
    portfolios = Portfolio.objects.filter(user=user)
    data = dict()
    data['result'] = render_to_string(
        template_name='ajax/portfolios_modal.html',
        request=request,
        context={
            'portfolios': portfolios,
            'strategy': strategy
        }
    )
    return JsonResponse(data)


