from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import UserDateRange

@receiver(post_save, sender=UserDateRange)
def update_rest_date_range(sender, instance, **kwargs):
    setting = instance.settings
    if instance.is_primary:
        qs = UserDateRange.objects.filter(settings=setting).exclude(id=instance.id)
        qs.update(is_primary=False)