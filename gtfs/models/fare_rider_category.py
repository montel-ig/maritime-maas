"""
Based on GTFS+ 1.7
https://www.transitwiki.org/TransitWiki/images/e/e7/GTFS%2B_Additional_Files_Format_Ver_1.7.pdf


File Name - fare_rider_categories.txt

This file specifies attributes for the fares for rider categories. GTFS file
fare_attributes.txt contains the fares for the Regular rider category. Fares for
other rider categories such as Child, Senior, etc will be provided in this plus file
fare_rider_categories.txt. The combination of fare_id and rider_category_id should be
unique in this file. This file is needed because standard GTFS does not include these
fields.
"""

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModel, PriceModel
from .fare import Fare
from .rider_category import RiderCategory


class FareRiderCategory(GTFSModel, PriceModel):
    fare = models.ForeignKey(Fare, verbose_name=_("fare"), on_delete=models.CASCADE)
    rider_category = models.ForeignKey(
        RiderCategory, verbose_name=_("fare"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("fare rider category")
        verbose_name_plural = _("fare rider categories")
        default_related_name = "fare_rider_categories"
        constraints = [
            models.UniqueConstraint(
                fields=["fare", "rider_category"],
                name="unique_fare_rider_category",
            )
        ]

    def __str__(self):
        return (
            f"{self.fare.agency} | "
            f"{self.rider_category} {self.price} {self.currency_type}"
        )
