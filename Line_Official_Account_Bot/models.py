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

    def __str__(self):
        return f"{self.location} - {self.start_time} to {self.end_time}"

class LineUserSessions(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_EXPIRED = 'expired'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'pending'),
        (STATUS_EXPIRED, 'expired'),
        (STATUS_COMPLETED, 'completed'),
    ]

    user_id = models.CharField(max_length=50)
    expiry_date = models.BigIntegerField()
    task = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # 在初始化物件時自動添加 5 分鐘
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not self.pk in kwargs:
            self.expiry_date = int(kwargs['expiry_date']) + 300000

    def __str__(self):
        return f"{self.user_id} - {self.task} - {self.status}"

    def is_pending(self, current_timestamp):
        return current_timestamp < self.expiry_date
