from django.contrib import admin

from .models import Portfolio, UserTicker, Ticker, Group
from import_export.admin import ImportExportModelAdmin



@admin.register(Portfolio)
class PortoAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTicker)
class UserTickerAdmin(admin.ModelAdmin):
    pass


@admin.register(Ticker)
class TickerAdmin(ImportExportModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin):
    pass
