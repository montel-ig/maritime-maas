from django.contrib import admin

from .models import (
    Agency,
    Calendar,
    CalendarDate,
    Departure,
    Fare,
    FareRule,
    Feed,
    Route,
    Stop,
    StopTime,
    Trip,
)


class FeedInline(admin.TabularInline):
    model = Feed
    extra = 0


admin.site.register(Agency)
admin.site.register(Calendar)
admin.site.register(CalendarDate)
admin.site.register(Departure)
admin.site.register(Fare)
admin.site.register(FareRule)
admin.site.register(Feed)
admin.site.register(Route)
admin.site.register(Stop)
admin.site.register(StopTime)
admin.site.register(Trip)
