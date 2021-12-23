from django.contrib import admin

from tickers.models import Portfolio, UserTicker, Ticker, Group, User
from .models import BackupSignature
from import_export import resources


class TickerResources(resources.ModelResource):

    class Meta:
        model = Ticker


class UserResources(resources.ModelResource):

    class Meta:
        model = User


class PortfolioResources(resources.ModelResource):

    class Meta:
        model = Portfolio


class UserTickerResources(resources.ModelResource):

    class Meta:
        model = UserTicker


@admin.register(BackupSignature)
class BackupSignatureAdmin(admin.ModelAdmin):
    pass