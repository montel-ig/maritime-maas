from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .agency import Agency
from .base import GTFSModelWithSourceID


class Route(GTFSModelWithSourceID):
    class Type(models.IntegerChoices):
        TRAM = 0, _("Tram")
        SUBWAY = 1, _("Subway")
        RAIL = 2, _("Rail")
        BUS = 3, _("Bus")
        FERRY = 4, _("Ferry")
        CABLE_TRAM = 5, _("Cable tram")
        AERIAL_LIFT = 6, _("Aerial lift")
        FUNICULAR = 7, _("Funicular")
        TROLLEYBUS = 11, _("Trolleybus")
        MONORAIL = 12, _("Monorail")

    agency = models.ForeignKey(
        Agency,
        verbose_name=_("agency"),
        on_delete=models.CASCADE,
    )
    short_name = models.CharField(
        verbose_name=_("short name"), max_length=32, blank=True
    )
    long_name = models.CharField(
        verbose_name=_("long name"), max_length=255, blank=True
    )
    desc = models.TextField(verbose_name=_("description"), blank=True)
    type = models.PositiveSmallIntegerField(
        verbose_name=_("type"), choices=Type.choices
    )
    url = models.URLField(verbose_name=_("URL"), blank=True)

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("route")
        verbose_name_plural = _("routes")
        default_related_name = "routes"

    def __str__(self):
        return self.short_name or self.long_name
