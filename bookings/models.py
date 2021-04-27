from urllib.parse import urljoin
from uuid import uuid4

import requests
from django.db import models
from django.utils.translation import gettext_lazy as _

from bookings.utils import TokenAuth
from gtfs.models.base import TimestampedModel
from maas.models import MaasOperator, TicketingSystem

BOOKING_TIMEOUT = 10


class BookingQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        return self.filter(maas_operator=maas_operator)

    def create_reservation(
        self,
        maas_operator: MaasOperator,
        ticketing_system: TicketingSystem,
        ticket_data: dict,
    ):
        # TODO MAP ticket data
        payload = {"ticket": "data"}
        response = requests.post(
            ticketing_system.api_url,
            json=payload,
            timeout=BOOKING_TIMEOUT,
            auth=TokenAuth(ticketing_system.api_key)
            if ticketing_system.api_key
            else None,
        )
        response.raise_for_status()
        response_data = response.json()

        return Booking.objects.create(
            source_id=response_data["id"],
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
        self.status = Booking.Status.CONFIRMED

        payload = {"id": self.source_id}
        response = requests.post(
            urljoin(self.ticketing_system.api_url, f"{self.source_id}/confirm/"),
            json=payload,
            timeout=BOOKING_TIMEOUT,
            auth=TokenAuth(self.ticketing_system.api_key)
            if self.ticketing_system.api_key
            else None,
        )
        response.raise_for_status()
        response_data = response.json()

        self.source_id = response_data["id"]
        self.save()
        return response_data.get("tickets", [])
