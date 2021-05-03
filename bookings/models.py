from urllib.parse import urljoin
from uuid import uuid4

import requests
from django.db import models
from django.utils.translation import gettext_lazy as _

from bookings.utils import TokenAuth
from gtfs.models.base import TimestampedModel
from maas.models import MaasOperator, TicketingSystem


class TicketingSystemAPI:
    TIMEOUT = 10

    def __init__(self, ticketing_system: TicketingSystem, maas_operator: MaasOperator):
        self.ticketing_system = ticketing_system
        self.maas_operator = maas_operator

    def reserve(self, ticket_data: dict):
        url = self.ticketing_system.api_url
        return self._post(url, ticket_data)

    def confirm(self, identifier: str):
        url = urljoin(self.ticketing_system.api_url, f"{identifier}/confirm/")

        return self._post(url, {})

    def _post(self, url: str, data):
        from bookings.serializers import ApiBookingSerializer

        payload = ApiBookingSerializer(
            {**data, "maas_operator": self.maas_operator}
        ).data

        if not self.ticketing_system.api_key:
            raise Exception("Ticketing system doesn't define an API key.")

        response = requests.post(
            url,
            json=payload,
            timeout=self.TIMEOUT,
            auth=TokenAuth(self.ticketing_system.api_key),
        )

        response.raise_for_status()
        return response.json()


class BookingQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        return self.filter(maas_operator=maas_operator)

    def create_reservation(
        self,
        maas_operator: MaasOperator,
        ticketing_system: TicketingSystem,
        ticket_data: dict,
    ):
        api = TicketingSystemAPI(ticketing_system, maas_operator)
        response_data = api.reserve(ticket_data)

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
        """Confirm the booking and return ticket information."""
        self.status = Booking.Status.CONFIRMED

        api = TicketingSystemAPI(self.ticketing_system, self.maas_operator)
        response_data = api.confirm(self.source_id)

        self.source_id = response_data["id"]
        self.save()
        return response_data.get("tickets", [])
