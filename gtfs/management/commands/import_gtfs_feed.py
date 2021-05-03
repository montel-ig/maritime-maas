from django.core.management import BaseCommand
from django.db import transaction

from gtfs.importers import GTFSFeedUpdater
from gtfs.models import Feed


class Command(BaseCommand):
    help = "Imports a GTFS feed based on an URL or a file path."

    def add_arguments(self, parser):
        parser.add_argument("url_or_path", type=str)
        parser.add_argument("--skip-validation", action="store_true")

    def handle(self, *args, **options):
        updater = GTFSFeedUpdater()
        url_or_path = options["url_or_path"]

        try:
            feed = Feed.objects.get(url_or_path=url_or_path)
        except Feed.DoesNotExist:
            feed = Feed(url_or_path=url_or_path)

        if not feed.pk:
            # when creating a new Feed obj, run the complete update in a transaction so
            # that the new obj won't be created in case of an error
            with transaction.atomic():
                feed.save()
                updater.update_single_feed(
                    feed, skip_validation=options["skip_validation"]
                )
        else:
            updater.update_single_feed(feed, skip_validation=options["skip_validation"])
