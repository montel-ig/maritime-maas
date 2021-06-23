from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .base import GTFSModelWithSourceID
from .route import Route
from .shape import Shape


class Trip(TranslatableModel, GTFSModelWithSourceID):
    class WheelchairAccessible(models.IntegerChoices):
        UNKNOWN = 0, _("Unknown")
        ACCESSIBLE = 1, _("Accessible")
        NOT_ACCESSIBLE = 2, _("Not accessible")

    class BikesAllowed(models.IntegerChoices):
        UNKNOWN = 0, _("Unknown")
        ALLOWED = 1, _("Allowed")
        NOT_ALLOWED = 2, _("Not allowed")

    translations = TranslatedFields(
        headsign=models.CharField(
            verbose_name=_("headsign"), max_length=255, blank=True
        ),
        short_name=models.CharField(
            verbose_name=_("short name"), max_length=64, blank=True
        ),
    )
    route = models.ForeignKey(Route, verbose_name=_("route"), on_delete=models.CASCADE)

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
    shape = models.ForeignKey(
        Shape, verbose_name=_("shape"), blank=True, null=True, on_delete=models.SET_NULL
    )
    block_id = models.CharField(verbose_name=_("block ID"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("trip")
        verbose_name_plural = _("trips")
        default_related_name = "trips"

    def __str__(self):
        return self.safe_translation_getter(
            "short_name", default=super().__str__, any_language=True
        )
