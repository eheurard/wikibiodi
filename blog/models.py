from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    ISIN_number = models.CharField(max_length=20, unique=True, null=True)
    Ticker = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sector = models.CharField(max_length=200)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

