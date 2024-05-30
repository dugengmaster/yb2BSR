from django.test import TestCase
from django.conf import settings
# Create your tests here.
configuration = Configuration(access_token=settings.LINE_CHANNEL_SECRET)
print(type(configuration))