import json
import logging
import paho.mqtt.client as mqtt
from decimal import Decimal
from asgiref.sync import async_to_sync

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer

from apps.acceso.models import AccessLog
from apps.pagos.models import PaymentLog

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run the MQTT client to listen to ESP32 events"

    def handle(self, *args, **options):
        client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)

        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        client.on_connect = self.on_connect
        client.on_message = self.on_message

        self.stdout.write(self.style.SUCCESS(f"Connecting to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}"))
        client.connect(
            host=settings.MQTT_BROKER_HOST,
            port=settings.MQTT_BROKER_PORT,
            keepalive=settings.MQTT_KEEPALIVE,
        )
        
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("MQTT client stopped."))
            client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("Connected successfully."))
            client.subscribe("esp32door/rfid/uid")
            client.subscribe("esp32cafe/rfid/uid")
            client.subscribe("esp32cafe/amount/set")
            self.cafe_amount = Decimal("0.00")
        else:
            self.stdout.write(self.style.ERROR(f"Connection failed with code {rc}"))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8').strip()
        logger.info(f"Received message on {topic}: {payload}")

        if topic == "esp32door/rfid/uid":
            self.process_access(client, payload)
        elif topic == "esp32cafe/amount/set":
            try:
                self.cafe_amount = Decimal(payload)
                self.stdout.write(self.style.SUCCESS(f"Cafeteria amount set to {self.cafe_amount}"))
            except ValueError:
                pass
        elif topic == "esp32cafe/rfid/uid":
            self.process_payment(client, payload)

    def process_access(self, client, rfid):
        try:
            user = User.objects.get(rfid_uid=rfid)
            if user.is_active:
                status = AccessLog.Status.AUTORIZADO
                name_to_send = user.name or user.email.split("@")[0]
                client.publish("esp32door/rfid/auth", f"autorizado-{name_to_send}")
            else:
                status = AccessLog.Status.NO_AUTORIZADO
                client.publish("esp32door/rfid/auth", "no autorizado")
        except User.DoesNotExist:
            user = None
            status = AccessLog.Status.NO_AUTORIZADO
            client.publish("esp32door/rfid/auth", "no autorizado")

        # Save to DB
        log = AccessLog.objects.create(rfid=rfid, status=status, user=user)

        # Send via channels
        channel_layer = get_channel_layer()
        log_data = {
            "id": log.id,
            "rfid": log.rfid,
            "timestamp": log.timestamp.isoformat(),
            "status": log.status,
            "nombre": user.name if user else "Desconocido",
            "anno_grado": getattr(user, "grade", ""),
            "seccion": getattr(user, "section", "")
        }
        async_to_sync(channel_layer.group_send)(
            "access_logs",
            {"type": "send_log", "log_data": log_data}
        )

    def process_payment(self, client, rfid):
        if getattr(self, "cafe_amount", Decimal("0.00")) <= Decimal("0.00"):
            client.publish("esp32cafe/rfid/auth", "error-monto")
            return

        try:
            user = User.objects.get(rfid_uid=rfid)
            if not user.is_active:
                status = PaymentLog.Status.ERROR
                client.publish("esp32cafe/rfid/auth", "error-usuario")
            elif user.balance >= self.cafe_amount:
                user.balance -= self.cafe_amount
                user.save()
                status = PaymentLog.Status.COMPLETADO
                client.publish("esp32cafe/rfid/auth", "pago_exitoso")
            else:
                status = PaymentLog.Status.SALDO_INSUFICIENTE
                client.publish("esp32cafe/rfid/auth", "saldo_insuficiente")
        except User.DoesNotExist:
            user = None
            status = PaymentLog.Status.ERROR
            client.publish("esp32cafe/rfid/auth", "error-usuario")

        # Save to DB
        log = PaymentLog.objects.create(rfid=rfid, status=status, amount=self.cafe_amount, user=user)

        # Send via channels
        channel_layer = get_channel_layer()
        payment_data = {
            "id": log.id,
            "rfid": log.rfid,
            "timestamp": log.timestamp.isoformat(),
            "status": log.status,
            "amount": float(log.amount),
            "nombre": user.name if user else "Desconocido"
        }
        async_to_sync(channel_layer.group_send)(
            "payment_logs",
            {"type": "send_payment", "payment_data": payment_data}
        )
