from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModelWithSourceID
from .route import Route


class Trip(GTFSModelWithSourceID):
    class WheelchairAccessible(models.IntegerChoices):
        UNKNOWN = 0, _("Unknown")
        ACCESSIBLE = 1, _("Accessible")
        NOT_ACCESSIBLE = 2, _("Not accessible")

    class BikesAllowed(models.IntegerChoices):
        UNKNOWN = 0, _("Unknown")
        ALLOWED = 1, _("Allowed")
        NOT_ALLOWED = 2, _("Not allowed")

    class CapacitySales(models.IntegerChoices):
        DISABLED = 0, _("Disabled")
        ENABLED = 1, _("Enabled")
        REQUIRED = 2, _("Required")

    route = models.ForeignKey(Route, verbose_name=_("route"), on_delete=models.CASCADE)
    headsign = models.CharField(verbose_name=_("headsign"), max_length=255, blank=True)
    short_name = models.CharField(
        verbose_name=_("short name"), max_length=64, blank=True
    )
    direction_id = models.PositiveSmallIntegerField(
        verbose_name=_("direction ID"), blank=True, null=True
    )
    wheelchair_accessible = models.PositiveSmallIntegerField(
        verbose_name=_("wheelchair accessible"),
        choices=WheelchairAccessible.choices,
        default=WheelchairAccessible.UNKNOWN,
    )
    bikes_allowed = models.PositiveSmallIntegerField(
        verbose_name=_("bikes allowed"),
        choices=BikesAllowed.choices,
        default=BikesAllowed.UNKNOWN,
    )
    capacity_sales = models.PositiveSmallIntegerField(
        verbose_name=_("capacity sales"),
        choices=CapacitySales.choices,
        default=CapacitySales.DISABLED,
    )

    class Meta:
        verbose_name = _("trip")
        verbose_name_plural = _("trips")
        default_related_name = "trips"

    def __str__(self):
        return self.short_name or super().__str__()
