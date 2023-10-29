from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from re import sub
from rest_framework.authtoken.models import Token


class ActiveUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token is not None:
            try:
                token = sub('Token ', '', header_token)
                token_obj = Token.objects.get(key = token)
                current_user = token_obj.user
                now = timezone.now()
                current_user.last_seen = now
                current_user.save()
            except Token.DoesNotExist:
                pass