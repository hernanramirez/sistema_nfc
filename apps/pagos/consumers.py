import json
import paho.mqtt.publish as publish
from asgiref.sync import sync_to_async
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

class PaymentLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "payment_logs"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "set_amount":
            amount = data.get("amount")
            if amount is not None:
                auth = None
                if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                    auth = {'username': settings.MQTT_USERNAME, 'password': settings.MQTT_PASSWORD}
                
                await sync_to_async(publish.single)(
                    "esp32cantina/pago/monto",
                    payload=str(amount),
                    hostname=settings.MQTT_BROKER_HOST,
                    port=settings.MQTT_BROKER_PORT,
                    keepalive=60,
                    auth=auth,
                    client_id=f"django_web_{self.channel_name.split('!')[-1][:8]}"
                )

    async def send_payment(self, event):
        payment_data = event["payment_data"]
        await self.send(text_data=json.dumps({"type": "payment_log", "data": payment_data}))
