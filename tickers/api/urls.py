from django.urls import path

from .views import (ticker_homepage_api_view,
                    TickerListApiView, TickerUpdateApiView,
                    PortfolioListApiView, PortfolioRetrieveUpdateDeleteApiView,
                    TickerAnalysisApiView,
                    UserTickerListApiView, UserTickerDetailApiView,
                    GroupListApiView, portfolio_total_data_view, UserTickerUpdateFromYahooApiView,
                    portfolio_refresh_data_view
                    )

app_name = 'api_tickers'

urlpatterns = [
    path('', ticker_homepage_api_view, name='home'),
    path('ticker/list/', TickerListApiView.as_view(), name='ticker_list'),
    path('ticker/update/<int:pk>/', TickerUpdateApiView.as_view(), name='ticker_update'),
    path('portfolio/list/', PortfolioListApiView.as_view(), name='portfolio_list'),
    path('portfolio/update-delete/<int:pk>/', PortfolioRetrieveUpdateDeleteApiView.as_view(), name='portfolio_update_delete'),
    path('portfolio/ticker/analysis/<int:pk>/', TickerAnalysisApiView.as_view(), name='ticker_analysis'),
    path('portfolio/user-ticker/', UserTickerListApiView.as_view(), name='user_ticker_list_view'),
    path('portfolio/user-ticker/detail/<int:pk>/', UserTickerDetailApiView.as_view(), name='user_ticker_detail_view'),
    path('group/list-create/', GroupListApiView.as_view(), name='group_list'),
    path('portfolio-total-data-by-user/', portfolio_total_data_view, name='portfolio_total_data_by_user'),
    path('user-ticker/update-from-api/<int:pk>/', UserTickerUpdateFromYahooApiView.as_view(), name='user_ticker_update_from_yahoo'),
    path('portfolio-refresh-data/<int:pk>/', portfolio_refresh_data_view, name='port_refresh_data'),

]