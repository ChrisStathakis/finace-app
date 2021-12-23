from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


from datetime import datetime


class ProfileSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class UserDateRange(models.Model):
    is_primary = models.BooleanField(default=False)
    settings = models.ForeignKey(ProfileSetting, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField(blank=True)

    def __str__(self):
        return f'{self.start} - {self.end}'

    def get_end(self):
        return self.end if self.end else datetime.now().date()

