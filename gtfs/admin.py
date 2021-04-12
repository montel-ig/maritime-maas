from django.contrib import admin

from .models import (
    Agency,
    Departure,
    Fare,
    FareRiderCategory,
    FareRule,
    Feed,
    RiderCategory,
    Route,
    Stop,
    StopTime,
    Trip,
)


class FeedInline(admin.TabularInline):
    model = Feed
    extra = 0


admin.site.register(Agency)
admin.site.register(Departure)
admin.site.register(Fare)
admin.site.register(FareRiderCategory)
admin.site.register(FareRule)
admin.site.register(Feed)
admin.site.register(RiderCategory)
admin.site.register(Route)
admin.site.register(Stop)
admin.site.register(StopTime)
admin.site.register(Trip)
