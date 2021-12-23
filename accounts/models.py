from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    starting_value = models.DecimalField(max_digits=30, decimal_places=4, blank=True, null=True, default=0)
    current_value = models.DecimalField(max_digits=30, decimal_places=4, blank=True, null=True, default=0)

    def __str__(self):
        return self.user.username