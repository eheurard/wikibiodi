from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    ISIN_number = models.CharField(max_length=20, unique=True, null=True)
    Ticker = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sector = models.CharField(max_length=200)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    asset_type = models.CharField(max_length=204, blank = True,null=True)
    owner_1 = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assets_owner1',null=True)
    ownership_1 = models.FloatField(null=True, blank=True)
    owner_2 = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assets_owner2', null=True, blank=True)
    owner_3 = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assets_owner3', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    water_score = models.FloatField(default=0,null=True, blank=True)
    biodiv_score = models.FloatField(default=0,null=True, blank=True)
    social_score = models.FloatField(default=0,null=True, blank=True)