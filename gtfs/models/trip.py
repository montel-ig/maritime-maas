from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields, TranslatableModel

from .base import GTFSModelWithSourceID
from .route import Route


class Trip(TranslatableModel, GTFSModelWithSourceID):
    translations = TranslatedFields(
        headsign=models.CharField(verbose_name=_("headsign"), max_length=255, blank=True),
        short_name=models.CharField(
            verbose_name=_("short name"), max_length=64, blank=True
        )
    )
    route = models.ForeignKey(Route, verbose_name=_("route"), on_delete=models.CASCADE)

    direction_id = models.PositiveSmallIntegerField(
        verbose_name=_("direction ID"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("trip")
        verbose_name_plural = _("trips")
        default_related_name = "trips"

    def __str__(self):
        return self.short_name or super().__str__()
