from django.http import HttpResponseNotFound
from django.template.loader import get_template

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            template = get_template('404.html')
            return HttpResponseNotFound(template.render())
        return response