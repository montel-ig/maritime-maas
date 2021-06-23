from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from gtfs.models.base import GTFSModelWithSourceID


class Agency(TranslatableModel, GTFSModelWithSourceID):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=64),
        url=models.URLField(verbose_name=_("URL")),
        phone=models.CharField(verbose_name=_("phone"), max_length=64, blank=True),
        fare_url=models.URLField(verbose_name=_("fare URL"), blank=True),
        email=models.EmailField(
            verbose_name=_("email"),
            blank=True,
        ),
    )
    timezone = models.CharField(
        verbose_name=_("timezone"), max_length=64, help_text=_("tz database time zone")
    )
    lang = models.CharField(
        verbose_name=_("language"),
        blank=True,
        max_length=16,
        help_text=_("IETF BCP 47 language code"),
    )
    logo_url = models.URLField(verbose_name=_("logo URL"), blank=True)

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("agency")
        verbose_name_plural = _("agencies")
        default_related_name = "agencies"

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=super().__str__, any_language=True
        )
