from django.urls import path

from .consumers import TickerConsumer

ws_urlpatterns = [
    path('ws/ticker/<slug:ticker_name>/', TickerConsumer.as_asgi())
    
    ]