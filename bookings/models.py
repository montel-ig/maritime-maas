from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from gtfs.models.base import TimestampedModel
from maas.models import MaasOperator, TicketingSystem


class BookingQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        return self.filter(maas_operator=maas_operator)

    def create_reservation(self, maas_operator, ticketing_system, *args, **kwargs):
        # TODO call ticketing system
        response = {"id": str(uuid4())}

        return Booking.objects.create(
            source_id=response["id"],
            maas_operator=maas_operator,
            ticketing_system=ticketing_system,
        )


class Booking(TimestampedModel):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", _("Reserved")
        CONFIRMED = "CONFIRMED", _("Confirmed")

    source_id = models.CharField(verbose_name=_("source ID"), max_length=255)
    api_id = models.UUIDField(verbose_name=_("API ID"), unique=True, default=uuid4)
    maas_operator = models.ForeignKey(
        MaasOperator, verbose_name=_("MaaS operator"), on_delete=models.PROTECT
    )
    ticketing_system = models.ForeignKey(
        TicketingSystem, verbose_name=_("ticketing system"), on_delete=models.PROTECT
    )
    status = models.CharField(
        verbose_name=_("status"),
        max_length=16,
        choices=Status.choices,
        default=Status.RESERVED,
    )

    objects = BookingQueryset.as_manager()

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        default_related_name = "bookings"
        constraints = [
            models.UniqueConstraint(
                fields=["ticketing_system", "source_id"],
                name="unique_booking_source_id",
            )
        ]

    def __str__(self):
        return f"Booking {self.api_id} ({self.status})"

    def confirm(self):
        # TODO call ticketing system
        self.status = Booking.Status.CONFIRMED
        self.save()
