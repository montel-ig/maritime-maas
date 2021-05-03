from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.managers import TranslatableQuerySet
from parler.models import TranslatableModel, TranslatedFields, TranslationDoesNotExist

from maas.models import MaasOperator

from .agency import Agency
from .base import GTFSModelWithSourceID
from .feed import Feed


class RouteQueryset(TranslatableQuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        feeds = Feed.objects.for_maas_operator(maas_operator)
        return self.filter(feed__in=feeds)


class Route(TranslatableModel, GTFSModelWithSourceID):
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

    class CapacitySales(models.IntegerChoices):
        DISABLED = 0, _("Disabled")
        ENABLED = 1, _("Enabled")
        REQUIRED = 2, _("Required")

    translations = TranslatedFields(
        long_name=models.CharField(
            verbose_name=_("long name"), max_length=255, blank=True
        ),
        desc=models.TextField(verbose_name=_("description"), blank=True),
        url=models.URLField(verbose_name=_("URL"), blank=True),
    )
    agency = models.ForeignKey(
        Agency,
        verbose_name=_("agency"),
        on_delete=models.CASCADE,
    )
    short_name = models.CharField(
        verbose_name=_("short name"), max_length=32, blank=True
    )
    type = models.PositiveSmallIntegerField(
        verbose_name=_("type"), choices=Type.choices
    )
    sort_order = models.PositiveSmallIntegerField(
        verbose_name=_("sort order"), null=True, blank=True
    )
    capacity_sales = models.PositiveSmallIntegerField(
        verbose_name=_("capacity sales"),
        choices=CapacitySales.choices,
        default=CapacitySales.DISABLED,
    )

    objects = RouteQueryset.as_manager()

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("route")
        verbose_name_plural = _("routes")
        default_related_name = "routes"

    def __str__(self):
        try:
            return self.short_name or self.safe_translation_getter(
                "long_name", any_language=True
            )
        except TranslationDoesNotExist:
            return self.super().__str__()
