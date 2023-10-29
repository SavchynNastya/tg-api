from re import sub
from django.http import request
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        header_token = None
        headers = scope['headers']
        for header in headers:
            if header[0] == b'authorization':
                header_token = header
        if header_token is not None:
            header_token = header_token[1].decode('utf-8')
            token = sub('Token ', '', header_token)
            scope['user'] = await self.get_user_from_token(token)
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None
        
TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

# @database_sync_to_async
# def get_user(token_key):
#     try:
#         token = Token.objects.get(key=token_key)
#         return token.user
#     except Token.DoesNotExist:
#         return AnonymousUser()

# class TokenAuthMiddleware(BaseMiddleware):
#     def __init__(self, inner):
#         super().__init__(inner)

#     async def __call__(self, scope, receive, send):
#         try:
#             token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
#         except ValueError:
#             token_key = None
#         scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
#         return await super().__call__(scope, receive, send)

# class TokenAuthMiddleware(BaseMiddleware):
#     def __init__(self, get_response):
#         self.get_response = get_response
        
#     async def __call__(self, scope=None, receive=None, send=None, request=None):
#         if scope:
#             header_token = None
#             headers = scope['headers']
#             for header in headers:
#                 if header[0] == b'authorization':
#                     header_token = header
#             if header_token is not None:
#                 header_token = header_token[1].decode('utf-8')
#                 token = sub('Token ', '', header_token)
#                 scope['user'] = await self.get_user_from_token(token)
#             return await super().__call__(scope, receive, send)
#         if request:
#             header_token = request.META.get('HTTP_AUTHORIZATION', None)
#             if header_token:
#                 token_key = sub('Token ', '', header_token)
#                 user = self.get_user_from_token_request(token_key)
#                 request.user = user
#                 response = self.get_response(request)
#                 return response

#     def get_user_from_token_request(self, token_key):
#         try:
#             token = Token.objects.get(key=token_key)
#             return token.user
#         except Token.DoesNotExist:
#             return AnonymousUser()

#     @database_sync_to_async
#     def get_user_from_token(self, token_key):
#         try:
#             token = Token.objects.get(key=token_key)
#             return token.user
#         except Token.DoesNotExist:
#             return None
        
# TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

# # @database_sync_to_async
# # def get_user(token_key):
# #     try:
# #         token = Token.objects.get(key=token_key)
# #         return token.user
# #     except Token.DoesNotExist:
# #         return AnonymousUser()

# # class TokenAuthMiddleware(BaseMiddleware):
# #     def __init__(self, inner):
# #         super().__init__(inner)

# #     async def __call__(self, scope, receive, send):
# #         try:
# #             token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
# #         except ValueError:
# #             token_key = None
# #         scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
# #         return await super().__call__(scope, receive, send)