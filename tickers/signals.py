from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import UserTicker, HistoricTicker, Ticker
from datetime import datetime


@receiver(post_save, sender=UserTicker)
def save_profile(sender, instance, created,**kwargs, ):
    # instance.portfolio.save() if instance.portfolio else ''
    ticker = instance.ticker

    '''
    if created:
        HistoricTicker.objects.create(
            ticker=instance,
            beta=ticker.beta,
            coverage=ticker.coverage,
            market_variance=ticker.market_variance,
            camp=ticker.camp,
            price=ticker.price,
            simply_return=ticker.simply_return,
            log_return=ticker.log_return,
            standard_deviation=ticker.standard_deviation,
        )
    qs = HistoricTicker.objects.filter(ticker=instance)
    if not qs and instance.is_buy:
        HistoricTicker.objects.create(
            ticker=instance,
            beta=ticker.beta,
            coverage=ticker.coverage,
            market_variance=ticker.market_variance,
            camp=ticker.camp,
            price=ticker.price,
            simply_return=ticker.simply_return,
            log_return=ticker.log_return,
            standard_deviation=ticker.standard_deviation,
        )
    '''


