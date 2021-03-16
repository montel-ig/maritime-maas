from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModel
from .calendar import Calendar


class CalendarDate(GTFSModel):
    class ExceptionType(models.IntegerChoices):
        ADDED = 0, _("Added")
        REMOVED = 1, _("Removed")

    calendar = models.ForeignKey(
        Calendar, related_name="calendar_dates", on_delete=models.CASCADE
    )
    date = models.DateField(verbose_name=_("date"))
    exception_type = models.PositiveSmallIntegerField(
        verbose_name=_("exception type"), choices=ExceptionType.choices
    )

    class Meta(GTFSModel.Meta):
        verbose_name = _("calendar date")
        verbose_name_plural = _("calendar dates")
        default_related_name = "calendar_dates"
        constraints = [
            models.UniqueConstraint(
                fields=["calendar", "date"],
                name="unique_calendar_date",
            )
        ]

    def __str__(self):
        return f"{self.date} | {self.get_exception_type_display()}"
