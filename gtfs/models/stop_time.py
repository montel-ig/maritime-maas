from datetime import datetime

from django.contrib.gis.db import models
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from pytz import timezone, utc

from .base import GTFSModel
from .stop import Stop
from .trip import Trip


class StopTime(TranslatableModel, GTFSModel):
    class Timepoint(models.IntegerChoices):
        APPROXIMATE = 0, _("Times are considered approximate")
        EXACT = 1, _("Times are considered exact")

    translations = TranslatedFields(
        stop_headsign=models.CharField(
            verbose_name=_("stop headsign"), max_length=255, blank=True
        )
    )
    trip = models.ForeignKey(Trip, verbose_name=_("trip"), on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, verbose_name=_("stop"), on_delete=models.CASCADE)

    # these are actually times not durations, but we cannot use TimeField because we
    # need to support GTFS times that can go past 24h
    arrival_time = models.DurationField(
        verbose_name=_("arrival time"), null=True, blank=True
    )
    departure_time = models.DurationField(
        verbose_name=_("departure time"), null=True, blank=True
    )

    stop_sequence = models.PositiveIntegerField(verbose_name=_("stop sequence"))
    timepoint = models.PositiveSmallIntegerField(
        verbose_name=_("timepoint"),
        choices=Timepoint.choices,
        default=Timepoint.EXACT,
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

    def get_arrival_time_datetime(self, departure):
        return self._get_time_datetime(self.arrival_time, departure)

    def get_departure_time_datetime(self, departure):
        return self._get_time_datetime(self.departure_time, departure)

    def _get_time_datetime(self, time, departure):
        return make_aware(
            datetime.combine(departure.date, datetime.min.time()) + time,
            timezone=timezone(departure.trip.route.agency.timezone),
        ).astimezone(utc)
