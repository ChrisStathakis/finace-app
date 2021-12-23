from django.db import models

# Create your models here.


class BackupSignature(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title