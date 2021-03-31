from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from maas.models import MaasOperator

from .base import GTFSModelWithSourceID
from .feed import Feed


class StopQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        feeds = Feed.objects.for_maas_operator(maas_operator)
        return self.filter(feed__in=feeds)


class Stop(GTFSModelWithSourceID):
    name = models.CharField(verbose_name=_("name"), max_length=255, blank=True)
    code = models.CharField(verbose_name=_("code"), max_length=255, blank=True)
    desc = models.TextField(verbose_name=_("description"), blank=True)
    point = models.PointField(verbose_name=_("point"))

    objects = StopQueryset.as_manager()

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("stop")
        verbose_name_plural = _("stops")
        default_related_name = "stops"

    def __str__(self):
        return self.name or super().__str__()
