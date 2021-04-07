from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base import GTFSModel
from .stop import Stop
from .trip import Trip


class StopTime(GTFSModel):
    trip = models.ForeignKey(Trip, verbose_name=_("trip"), on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, verbose_name=_("stop"), on_delete=models.CASCADE)
    arrival_time = models.TimeField(
        verbose_name=_("arrival time"), null=True, blank=True
    )
    departure_time = models.TimeField(
        verbose_name=_("departure time"), null=True, blank=True
    )
    stop_sequence = models.PositiveIntegerField(verbose_name=_("stop sequence"))
    stop_headsign = models.CharField(
        verbose_name=_("stop headsign"), max_length=255, blank=True
    )

    class Meta:
        verbose_name = _("stop times")
        verbose_name_plural = _("stop times")
        default_related_name = "stop_times"
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "stop_sequence"],
                name="unique_stop_sequence",
            )
        ]

    def __str__(self):
        return (
            f"{self.trip} | {self.stop_sequence} | {self.stop} | {self.arrival_time}"
            + (
                f" | {self.departure_time}"
                if self.departure_time != self.arrival_time
                else ""
            )
        )
