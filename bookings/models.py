from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.utils.context import switch_language

from bookings.choices import BookingStatus
from bookings.ticketing_system import TicketingSystemAPI
from gtfs.models.base import TimestampedModel
from maas.models import MaasOperator, TicketingSystem


class BookingQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        return self.filter(maas_operator=maas_operator)

    def create_reservation(
        self,
        maas_operator: MaasOperator,
        ticketing_system: TicketingSystem,
        ticket_data: dict,
    ):
        with switch_language(ticket_data["route"], "fi"):
            route_name = ticket_data["route"].long_name
        ticket_count = len(ticket_data["tickets"])
        transaction_id = ticket_data.get("transaction_id", "")

        api = TicketingSystemAPI(ticketing_system, maas_operator)
        response_data = api.reserve(ticket_data)

        return Booking.objects.create(
            source_id=response_data["id"],
            maas_operator=maas_operator,
            ticketing_system=ticketing_system,
            route_name=route_name,
            ticket_count=ticket_count,
            transaction_id=transaction_id,
        )


class Booking(TimestampedModel):
    Status = BookingStatus  # solving circular importing issues beautifully here
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
    route_name = models.CharField(
        verbose_name=_("route name"),
        max_length=255,
        blank=True,
        help_text=_("Name of the route for which the booking was made."),
    )
    transaction_id = models.CharField(
        verbose_name=_("transaction ID"), max_length=255, blank=True
    )
    ticket_count = models.PositiveSmallIntegerField(
        _("ticket count"),
        default=0,
        help_text=_(
            "The amount of tickets that were requested from the ticketing system."
        ),
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

    def confirm(self, passed_parameters=None):
        """Confirm the booking and return ticket information."""
        passed_parameters = passed_parameters or {}
        self.status = Booking.Status.CONFIRMED

        api = TicketingSystemAPI(self.ticketing_system, self.maas_operator)
        response_data = api.confirm(self.source_id, passed_parameters=passed_parameters)

        self.source_id = response_data["id"]
        if transaction_id := passed_parameters.get("transaction_id"):
            self.transaction_id = transaction_id
        self.save()
        return response_data.get("tickets", [])
