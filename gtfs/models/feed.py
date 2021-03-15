from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import TimeStampedModel


class Feed(TimeStampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=255)

    class Meta:
        verbose_name = _("feed")
        verbose_name_plural = _("feeds")

    def __str__(self):
        return self.name
