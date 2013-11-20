from django.db import models

class Zipcode(models.Model):
    country_code = models.CharField(max_length=10)
    postal_code = models.CharField(max_length=20)
    place_name = models.CharField(max_length=255)
    admin_name1 = models.CharField(max_length=100)
    admin_code1 = models.CharField(max_length=100)
    admin_name2 = models.CharField(max_length=100)
    admin_code2 = models.CharField(max_length=100)
    admin_name3 = models.CharField(max_length=100)
    admin_code3 = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    def __unicode__(self):
        return self.postal_code
