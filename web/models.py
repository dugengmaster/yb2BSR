from django.db import models
from django.contrib.auth.models import User



first_user = User.objects.first()
class UserProfile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=first_user)
    line_user_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    telecom = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     is_first_login = models.BooleanField(default=True)
#     access_token = models.CharField(max_length=200)
#     bio = models.TextField(default='This is my bio')
#     carrier = models.CharField(max_length=100, blank=True, null=True)




