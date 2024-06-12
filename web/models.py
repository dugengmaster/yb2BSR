from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=200)
    bio = models.TextField(default='This is my bio')

    def __str__(self):
        return self.user.username
