from re import sub
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from django.middleware.csrf import get_token

class ApiTokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header_token = request.META.get('HTTP_AUTHORIZATION', None)

        if header_token:
            token_key = sub('Token ', '', header_token)
            user = self.get_user_from_token(token_key)
            request.user = user

        response = self.get_response(request)
        return response

    def get_user_from_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()