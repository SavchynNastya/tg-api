import os
from django.core.asgi import get_asgi_application
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from tg_api.middleware import TokenAuthMiddleware
from chats.consumers import ChatConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tg_api.settings')
django.setup()


django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': 
    # AllowedHostsOriginValidator(
            # AuthMiddlewareStack(
                TokenAuthMiddleware(
                    URLRouter([
                        path('ws/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
                    ]),
            ),
        # ),
    # ),
})
