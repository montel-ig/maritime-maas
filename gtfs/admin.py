import logging

from django.contrib import admin, messages
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from requests import RequestException

from .importers import GTFSFeedUpdater
from .importers.gtfs_feed_importer import GTFSFeedImporterError
from .models import (
    Agency,
    Departure,
    Fare,
    FareRiderCategory,
    FareRule,
    Feed,
    FeedInfo,
    RiderCategory,
    Route,
    Shape,
    Stop,
    StopTime,
    Trip,
)

logger = logging.getLogger(__name__)


class FeedInline(admin.TabularInline):
    model = Feed
    extra = 0


class FeedInfoInline(admin.StackedInline):
    model = FeedInfo
    extra = 0


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url_or_path",
        "imported_at",
        "import_attempted_at",
        "last_import_successful",
    )
    list_display_links = ("name", "url_or_path")
    inlines = [FeedInfoInline]
    actions = ("update_feed",)
    readonly_fields = (
        "created_at",
        "imported_at",
        "import_attempted_at",
        "last_import_successful",
        "last_import_error_message",
    )

    def last_import_successful(self, obj):
        return obj.last_import_successful

    last_import_successful.boolean = True

    def routes(self, obj):
        return obj.routes.count()

    def stops(self, obj):
        return obj.stops.count()

    def trips(self, obj):
        return obj.trips.count()

    def departures(self, obj):
        return Departure.objects.filter(trip__feed=obj).count()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return ((None, {"fields": ("name", "url_or_path")}),)

        import_fields = ("imported_at", "import_attempted_at", "last_import_successful")
        if obj.last_import_successful is False:
            import_fields += ("last_import_error_message",)

        return (
            (
                None,
                {"fields": ("name", "url_or_path", "created_at")},
            ),
            (
                _("Import"),
                {
                    "fields": import_fields,
                },
            ),
        )

    def update_feed(self, request, queryset):
        feed_updater = GTFSFeedUpdater()
        success = True

        for feed in queryset:
            try:
                feed_updater.update_single_feed(feed, force=True)
            except (RequestException, GTFSFeedImporterError) as e:
                logger.exception(f'Failed to update feed: "{feed.name}"')
                self.message_user(
                    request,
                    _(f'Failed to update feed: "{feed.name}": {e}'),
                    messages.ERROR,
                )
                success = False

        if success:
            self.message_user(request, _("Selected feeds updated."), messages.SUCCESS)

    update_feed.short_description = _("Update selected feeds")


@admin.register(Shape)
class ShapeAdmin(OSMGeoAdmin):
    pass


admin.site.register(Agency, TranslatableAdmin)
admin.site.register(Departure)
admin.site.register(Fare)
admin.site.register(FareRiderCategory)
admin.site.register(FareRule)
admin.site.register(RiderCategory)
admin.site.register(Route, TranslatableAdmin)
admin.site.register(Stop, TranslatableAdmin)
admin.site.register(StopTime, TranslatableAdmin)
admin.site.register(Trip, TranslatableAdmin)
