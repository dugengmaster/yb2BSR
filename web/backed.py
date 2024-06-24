from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile

class LineUserBackend(BaseBackend):
    def authenticate(self, request, line_user_id=None):
        try:
            user = UserProfile.objects.get(line_user_id=line_user_id)
            return user
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            return None