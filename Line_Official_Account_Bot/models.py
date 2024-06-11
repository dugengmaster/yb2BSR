from typing import Any
from django.db import models

# Create your models here.

class WeatherRecord(models.Model):
    location = models.CharField(max_length=50)
    start_time = models.BigIntegerField()
    end_time = models.BigIntegerField()
    wx = models.CharField(max_length=50, null=True, blank=True)
    weather_code = models.CharField(max_length=10, null=True, blank=True)
    pop_value = models.CharField(max_length=10, null=True, blank=True)
    pop_unit = models.CharField(max_length=10, null=True, blank=True)
    min_temp = models.CharField(max_length=10, null=True, blank=True)
    max_temp = models.CharField(max_length=10, null=True, blank=True)
    temp_unit = models.CharField(max_length=5, null=True, blank=True)


class LineUserSessions(models.Model):
    user_id = models.CharField(max_length=50)
    expiry_date = models.BigIntegerField()
    task = models.CharField(max_length=255)

    # 在儲存階段時自動添加 5 分鐘到 expiry_date 供之後檢查 session 是否過期。
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.expiry_date += 300000
        super().save(force_insert, force_update, using, update_fields)

class WeatherCodeImage(models.Model):
    weather_code = models.CharField(max_length=10, unique=True)
    image_url = models.URLField()
