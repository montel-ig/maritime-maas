from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModel


class Agency(GTFSModel):
    name = models.CharField(verbose_name=_("name"), max_length=64)
    url = models.URLField(verbose_name=_("URL"))
    timezone = models.CharField(
        verbose_name=_("timezone"), max_length=64, help_text=_("tz database time zone")
    )
    lang = models.CharField(
        verbose_name=_("language"),
        blank=True,
        max_length=16,
        help_text=_("IETF BCP 47 language code"),
    )
    phone = models.CharField(verbose_name=_("phone"), max_length=64, blank=True)
    fare_url = models.URLField(verbose_name=_("fare URL"), blank=True)
    email = models.EmailField(
        verbose_name=_("email"),
        blank=True,
    )

    class Meta(GTFSModel.Meta):
        verbose_name = _("agency")
        verbose_name_plural = _("agencies")
        default_related_name = "agencies"

    def __str__(self):
        return self.name
