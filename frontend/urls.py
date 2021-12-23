from django.urls import path

from .views import (homepage, login_view, StrategyView, moving_average_trading_strategy_view,
                    add_ticker_to_strategy_view, delete_ticker_from_strategy_view,

                    )

from .ajax_views import ajax_show_portfolios_view
from .action_views import add_portfolio_to_strategy_view


urlpatterns = [
    path('', homepage, name='homepage'),
    path('login/', login_view, name='login'),

    # strategies
    path('strategies/', StrategyView.as_view(), name='strategy_homepage'),
    path('strategies/moving-average-trading-strategy/', moving_average_trading_strategy_view, name='moving_average_trading'),
    path('strategies/add-to-strategy-ticker/<int:pk>/<int:dk>/', add_ticker_to_strategy_view, name='add_to_strategy_ticker'),
    path('strategies/delete-ticker-from-strategy/<int:pk>/', delete_ticker_from_strategy_view, name='remove_ticker_from_strategy'),

    # action views
    path('strategies/add-port-to-strategy/<int:pk>/<int:dk>/', add_portfolio_to_strategy_view, name='add_portfolio_to_strategy'),

    # ajax views
    path('strategies/ajax/show-portfolio/<int:pk>/', ajax_show_portfolios_view, name='ajax_portfolios_modal')
]