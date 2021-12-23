from django.urls import path

from .views import (portofolio_view, TickerListView, TickerUpdateView, ticker_delete_view,
                    PortfoliosListView)

from .validate_views import validate_create_ticker_form, validate_create_group_form, validate_portfolio_create_form
from .actions import (refresh_ticker_data, refresh_portfolio_action_view, validate_ticker_create_from_portfolio_view,
                      refresh_tickers_data, buy_tickers_from_effective_frontier_view, update_ticker_api_view,
                      delete_ticker_from_portfolio_view, update_user_ticker_view, delete_portfolio_view,
                      add_random_tickers_to_portfolio
                      )
from .ajax_views import (ajax_add_ticker_modal, ajax_portfolio_effective_frontier_view, ajax_show_historic_graph,
                         search_tickers, create_random_portfolios_view, ajax_ticker_modal,ajax_refresh_portfolio_data
                         )

app_name = 'portfolio'

urlpatterns = [
    path('<int:id>/', portofolio_view, name='portofolio_detail'),

    path('tickers/', TickerListView.as_view(), name='ticker_list_view'),
    path('tickers/update/<int:pk>/', TickerUpdateView.as_view(), name='ticker_update'),
    path('tickers/delete/<int:id>/', ticker_delete_view, name='ticker_delete_view'),

    path('portfolios-list-view/', PortfoliosListView.as_view(), name='portfolio_list_view'),
    path('portfolio/delete/<int:pk>/', delete_portfolio_view, name='delete_portfolio'),

    path('validate/create-ticker/', validate_create_ticker_form, name='validate_create_ticker'),
    path('validate/create-group/', validate_create_group_form, name='validate_create_group'),
    path('validate/create-portfolio/', validate_portfolio_create_form, name='validate_create_portfolio'),

    path('validate/create-ticker-from-portfolio/<int:pk>/<int:dk>/', validate_ticker_create_from_portfolio_view,
         name='validate_create_ticker_from_portfolio'),

    path('add-tickers-to-portfolio-frontier/<int:pk>/', buy_tickers_from_effective_frontier_view,
         name='buy_tickers_effective_frontier'),

    path('update-ticker-action/<int:pk>/<slug:slug>/', update_ticker_api_view, name='update_ticker_api_view'),
    path('delete-ticker-from-portfolio/<int:pk>/', delete_ticker_from_portfolio_view,
         name='delete_ticker_from_portfolio'),

    path('update-ticker-from-portfolio/<int:pk>/', update_user_ticker_view, name='update_user_ticker'),

    path('refresh-ticker-data/<int:pk>/', refresh_ticker_data, name='refresh_ticker_data'),
    path('refresh-tickers-data/', refresh_tickers_data, name='refresh_tickers_data'),
    path('refresh-portfolio-tickers/<int:pk>/', refresh_portfolio_action_view, name='refresh_portfolio_tickers'),

    path('ajax/create-ticker-modal/<int:pk>/<int:dk>/', ajax_add_ticker_modal, name='ajax_add_ticker_modal'),
    path('ajax/portfolio/effective-frontier/<int:pk>/', ajax_portfolio_effective_frontier_view, name='ajax_effective_frontier'),
    path('ajax/show-graph/<int:pk>/', ajax_show_historic_graph, name='ajax_show_graph'),
    path('ajax/search-tickers/<int:pk>/', search_tickers, name='ajax-search_tickers'),
    path('create-random-portfolio-tickers/<int:pk>/', create_random_portfolios_view, name='create_random_port_tickers'),

    path('add-random-tickers-to-portfolio/<int:pk>/', add_random_tickers_to_portfolio, name='add_random_tickers_to_portfolio'),
    path('ajax-show-ticker-modal/<int:pk>/<int:dk>/', ajax_ticker_modal, name='ajax_show_ticker_modal'),
    path('ajax/update-ticker-data/<int:pk>/', ajax_refresh_portfolio_data, name='ajax_refresh_portfolio_ticker_data'),


  
    # strategies



]