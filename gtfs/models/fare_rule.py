from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModel
from .fare import Fare
from .route import Route


class FareRule(GTFSModel):
    fare = models.ForeignKey(Fare, verbose_name=_("fare"), on_delete=models.CASCADE)
    route = models.ForeignKey(
        Route, verbose_name=_("route"), blank=True, null=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("fare rule")
        verbose_name_plural = _("fare rules")
        default_related_name = "fare_rules"
