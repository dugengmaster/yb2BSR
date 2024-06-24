# from django.db import models
# from django.contrib.auth.models import User



# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)

#     line_user_id = models.CharField(max_length=100, blank=True, null=True)
#     line_name = models.CharField(max_length=150, blank=True, null=True)
#     email = models.EmailField(blank=True, null=True)
#     username = models.CharField(max_length=150, blank=True, null=True)
#     password = models.CharField(max_length=128, blank=True, null=True)
#     telecom = models.CharField(max_length=100, blank=True, null=True)
#     registration_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
#     last_login_date = models.DateTimeField(auto_now=True, blank=True, null=True)

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, line_user_id=None, password=None, **extra_fields):
        if not username and not line_user_id:
            raise ValueError('Either username or line_user_id must be set')

        user = self.model(
            username=username,
            line_user_id=line_user_id,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        user = self.create_user(
            username=username,
            password=password,
            **extra_fields
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser):
    line_user_id = models.CharField(max_length=100, blank=True, null=True)
    line_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    telecom = models.CharField(max_length=100, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['line_user_id']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return False

