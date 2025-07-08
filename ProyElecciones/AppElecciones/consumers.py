from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template


class TestConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("novedades", self.channel_name)
        print(f"Agregado {self.channel_name} canal a novedades")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("novedades", self.channel_name)
        print(f"Removido {self.channel_name} canal de novedades")

    async def user_gossip(self, event):
        await self.send_json(event)
        # print(f"Got message {event} at {self.channel_name}")

    async def publicar_novedad(self, event):
        # print(event['datos'])
        # html = get_template("AppElecciones/novedadesgenerales/notificacion_novedad.html").render(
        #     context={"mi_novedad": event["datos"]}
        # )
        await self.send_json(event["datos"])

    async def publicar_datos(self, event):
        # await self.send_json({'mensaje': 'hola desde la funcion'})
        await self.send_json(event["datos_logueo"])

