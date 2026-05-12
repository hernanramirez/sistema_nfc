from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class PaymentLog(models.Model):
    class Status(models.TextChoices):
        COMPLETADO = "completado", _("Completado")
        SALDO_INSUFICIENTE = "saldo insuficiente", _("Saldo Insuficiente")
        ERROR = "error", _("Error")

    rfid = models.CharField(_("RFID UID"), max_length=50)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    status = models.CharField(_("Status"), max_length=25, choices=Status.choices)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_logs")

    class Meta:
        verbose_name = _("Payment Log")
        verbose_name_plural = _("Payment Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.rfid} - {self.amount} - {self.status} at {self.timestamp}"
