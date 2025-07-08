"""
ASGI config for ProyElecciones project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

import AppElecciones.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyElecciones.settings')

django_app_asgi = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_app_asgi,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(AppElecciones.routing.websocket_urlpatterns))
    ),
})