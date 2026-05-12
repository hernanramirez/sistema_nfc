
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DecimalField, ManyToManyField, TextChoices
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Sistema LoT integrado.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    class Role(TextChoices):
        ALUMNO = "alumno", _("Alumno")
        DOCENTE = "docente", _("Docente")
        ADMINISTRATIVO = "administrativo", _("Personal Administrativo")
        DIRECCION = "direccion", _("Dirección")
        CAFETIN = "cafetin", _("Cafetería")
        REPRESENTANTE = "representante", _("Representante")

    role = CharField(_("Role"), max_length=20, choices=Role.choices, default=Role.ALUMNO)
    rfid_uid = CharField(_("RFID UID"), max_length=50, unique=True, null=True, blank=True)
    grade = CharField(_("Grade"), max_length=50, null=True, blank=True)
    section = CharField(_("Section"), max_length=50, null=True, blank=True)
    balance = DecimalField(_("Balance"), max_digits=10, decimal_places=2, default=0.00)
    represented_students = ManyToManyField("self", symmetrical=False, related_name="representatives", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
