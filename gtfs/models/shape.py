from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from maas.models import MaasOperator

from .base import GTFSModelWithSourceID
from .feed import Feed


class ShapeQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        feeds = Feed.objects.for_maas_operator(maas_operator)
        return self.filter(feed__in=feeds)


class Shape(GTFSModelWithSourceID):
    geometry = models.LineStringField(verbose_name=_("geometry"))

    objects = ShapeQueryset.as_manager()

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("shape")
        verbose_name_plural = _("shapes")
        default_related_name = "shapes"

    def __str__(self):
        return self.source_id
