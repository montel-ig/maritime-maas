from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModel


class Calendar(GTFSModel):
    class DayAvailability(models.IntegerChoices):
        NOT_AVAILABLE = 0, _("Not available")
        AVAILABLE = 1, _("Available")

    monday = models.PositiveSmallIntegerField(
        verbose_name=_("monday"), choices=DayAvailability.choices
    )
    tuesday = models.PositiveSmallIntegerField(
        verbose_name=_("Tuesday"), choices=DayAvailability.choices
    )
    wednesday = models.PositiveSmallIntegerField(
        verbose_name=_("Wednesday"), choices=DayAvailability.choices
    )
    thursday = models.PositiveSmallIntegerField(
        verbose_name=_("Thursday"), choices=DayAvailability.choices
    )
    friday = models.PositiveSmallIntegerField(
        verbose_name=_("Friday"), choices=DayAvailability.choices
    )
    saturday = models.PositiveSmallIntegerField(
        verbose_name=_("Saturday"), choices=DayAvailability.choices
    )
    sunday = models.PositiveSmallIntegerField(
        verbose_name=_("Sunday"), choices=DayAvailability.choices
    )
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"))

    class Meta(GTFSModel.Meta):
        verbose_name = _("calendar")
        verbose_name_plural = _("calendars")
        default_related_name = "calendars"

    def __str__(self):
        return f"{self.start_date} – {self.end_date}"
