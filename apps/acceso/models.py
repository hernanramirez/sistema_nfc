from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class AccessLog(models.Model):
    class Status(models.TextChoices):
        AUTORIZADO = "autorizado", _("Autorizado")
        NO_AUTORIZADO = "no autorizado", _("No Autorizado")

    rfid = models.CharField(_("RFID UID"), max_length=50)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="access_logs")

    class Meta:
        verbose_name = _("Access Log")
        verbose_name_plural = _("Access Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.rfid} - {self.status} at {self.timestamp}"
