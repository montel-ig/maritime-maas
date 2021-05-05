"""
Based on GTFS+ 1.7
https://www.transitwiki.org/TransitWiki/images/e/e7/GTFS%2B_Additional_Files_Format_Ver_1.7.pdf

File Name - rider_categories.txt

This file lists the rider categories for fares other than the Regular category.
This file is needed because standard GTFS does not include these fields.

"""
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields, TranslationDoesNotExist

from .base import GTFSModelWithSourceID


class RiderCategory(TranslatableModel, GTFSModelWithSourceID):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255),
        description=models.CharField(verbose_name=_("description"), max_length=255),
    )
    fares = models.ManyToManyField(
        "gtfs.Fare",
        verbose_name=_("fares"),
        related_name="rider_categories",
        through="gtfs.FareRiderCategory",
        blank=True,
    )

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("rider category")
        verbose_name_plural = _("rider categories")

    def __str__(self):
        try:
            return self.safe_translation_getter("name", any_language=True)
        except TranslationDoesNotExist:
            return super().__str__()
