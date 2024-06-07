from django.db import models

# Create your models here.

class WeatherRecord(models.Model):
    location = models.CharField(max_length=100)
    start_time = models.BigIntegerField()
    end_time = models.BigIntegerField()
    wx = models.CharField(max_length=50, null=True, blank=True)
    weather_code = models.CharField(max_length=10, null=True, blank=True)
    pop_value = models.CharField(max_length=10, null=True, blank=True)
    pop_unit = models.CharField(max_length=10, null=True, blank=True)
    min_temp = models.CharField(max_length=10, null=True, blank=True)
    max_temp = models.CharField(max_length=10, null=True, blank=True)
    temp_unit = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return f"{self.location} - {self.start_time} to {self.end_time}"
