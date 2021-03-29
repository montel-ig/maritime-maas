from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel


class Feed(TimeStampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=255)
    ticketing_system = models.ForeignKey(
        "maas.TicketingSystem",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("ticketing system"),
    )

    class Meta:
        verbose_name = _("feed")
        verbose_name_plural = _("feeds")
        default_related_name = "feeds"

    def __str__(self):
        return self.name
