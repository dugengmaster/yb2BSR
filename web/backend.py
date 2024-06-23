from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileBackend(BaseBackend):
    def authenticate(self, request, line_user_id=None):
        if line_user_id is None:
            return None
        try:
            user_profile = UserProfile.objects.get(line_user_id=line_user_id)
            return user_profile.user
        except UserProfile.DoesNotExist:
            return None

    def get_user(self, line_user_id):
        try:
            user_profile = UserProfile.objects.get(line_user_id=line_user_id)
            return user_profile.user
        except UserProfile.DoesNotExist:
            return None