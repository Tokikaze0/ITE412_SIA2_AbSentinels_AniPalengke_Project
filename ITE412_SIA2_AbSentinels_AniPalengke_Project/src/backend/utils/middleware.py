from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class CorsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            self.add_cors_headers(response)
            return response
        return None

    def process_response(self, request, response):
        self.add_cors_headers(response)
        return response

    def add_cors_headers(self, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response
