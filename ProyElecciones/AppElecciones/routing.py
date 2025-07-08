from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/novedades/", consumers.TestConsumer.as_asgi()),

]