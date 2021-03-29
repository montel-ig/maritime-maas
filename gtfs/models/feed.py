from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from maas.models import MaasOperator

from .base import TimeStampedModel


class FeedQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        return self.filter(
            ticketing_system__transport_service_providers__maas_operators=maas_operator
        )


class Feed(TimeStampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=255)
    ticketing_system = models.ForeignKey(
        "maas.TicketingSystem",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("ticketing system"),
    )

    objects = FeedQueryset.as_manager()

    class Meta:
        verbose_name = _("feed")
        verbose_name_plural = _("feeds")
        default_related_name = "feeds"

    def __str__(self):
        return self.name
