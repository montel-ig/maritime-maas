from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModelWithSourceID


class Stop(GTFSModelWithSourceID):
    name = models.CharField(verbose_name=_("name"), max_length=255, blank=True)
    code = models.CharField(verbose_name=_("code"), max_length=255, blank=True)
    desc = models.TextField(verbose_name=_("description"), blank=True)
    point = models.PointField(verbose_name=_("point"))

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("stop")
        verbose_name_plural = _("stops")
        default_related_name = "stops"

    def __str__(self):
        return self.name or super().__str__()
