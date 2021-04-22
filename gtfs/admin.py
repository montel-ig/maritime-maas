from django.contrib import admin
from parler.admin import TranslatableAdmin

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


class AgencyAdmin(TranslatableAdmin):
    fieldsets = (
        ("Translatable", {
            'fields': ('name', 'url', 'phone', 'fare_url', 'email'),
        }),
        ("Non-translatable", {
            'fields': ('timezone', 'lang'),
        })
    )


class RouteAdmin(TranslatableAdmin):
    fieldsets = (
        ("Translatable", {
            'fields': ('long_name', 'desc', 'url'),
        }),
        ("Non-translatable", {
            'fields': ('agency', 'short_name', 'type'),
        })
    )


class StopTimeAdmin(TranslatableAdmin):
    fieldsets = (
        ("Translatable", {
            'fields': ['headsign'],
        }),
        ("Non-translatable", {
            'fields': ('trip', 'stop', 'arrival_time', 'departure_time', 'stop_sequence'),
        })
    )


class StopAdmin(TranslatableAdmin):
    fieldsets = (
        ("Translatable", {
            'fields': ('name', 'desc'),
        }),
        ("Non-translatable", {
            'fields': ('code', 'point'),
        })
    )


class TripAdmin(TranslatableAdmin):
    fieldsets = (
        ("Translatable", {
            'fields': ('headsign', 'short_name'),
        }),
        ("Non-translatable", {
            'fields': ('route', 'direction_id'),
        })
    )


admin.site.register(Agency, AgencyAdmin)
admin.site.register(Departure)
admin.site.register(Fare)
admin.site.register(FareRiderCategory)
admin.site.register(FareRule)
admin.site.register(Feed)
admin.site.register(RiderCategory)
admin.site.register(Route, RouteAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(StopTime, StopTimeAdmin)
admin.site.register(Trip, TripAdmin)





