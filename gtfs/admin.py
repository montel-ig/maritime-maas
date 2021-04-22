import logging

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from requests import RequestException
from django.contrib import admin
from parler.admin import TranslatableAdmin


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
    inlines = [FeedInfoInline]
    actions = ("update_feed",)

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
                    _(f'Failed to update feed:"{feed.name}": {e}.'),
                    messages.ERROR,
                )
                success = False

        if success:
            self.message_user(request, _("Selected feeds updated."), messages.SUCCESS)

    update_feed.short_description = _("Update selected feeds")


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





