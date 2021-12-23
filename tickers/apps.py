from django.apps import AppConfig


class TickersConfig(AppConfig):
    name = 'tickers'

    def ready(self):
        import tickers.signals
