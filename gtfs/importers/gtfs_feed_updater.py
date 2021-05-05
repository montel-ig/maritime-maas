import logging

from django.db import transaction
from django.utils import timezone
from requests import RequestException

from gtfs.importers import GTFSFeedImporter
from gtfs.importers.gtfs_feed_importer import GTFSFeedImporterError
from gtfs.importers.gtfs_feed_reader import GTFSFeedReader
from gtfs.models import Feed


class GTFSFeedUpdater:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.importer = GTFSFeedImporter()
        self.reader = GTFSFeedReader()

    def update_feeds(self, force: bool = False):
        for feed in Feed.objects.all():
            try:
                self.update_single_feed(feed, force=force)
            except (RequestException, GTFSFeedImporterError):
                self.logger.exception(f'Failed to update feed: "{feed.name}"')

    def update_single_feed(
        self, feed: Feed, force: bool = False, skip_validation: bool = False
    ):
        imported = False

        with transaction.atomic():
            try:
                fingerprint = self.reader.get_feed_fingerprint(feed)
                if fingerprint != feed.fingerprint or force:
                    self.importer.run(feed, skip_validation)
                    imported = True
                else:
                    self.logger.info(
                        f'No need to update feed "{feed.name}", same fingerprint: "{feed.fingerprint}"'
                    )
            # catch everything so that even for bugs the feed's last import status is
            # correctly set to unsuccessful
            except Exception as e:  # noqa
                feed.last_import_error_message = str(e)
                feed.import_attempted_at = timezone.now()
                exception = e
            else:
                feed.last_import_error_message = ""
                if imported:
                    # after an actual successful import make import_attempted_at match
                    # its time exactly
                    feed.import_attempted_at = feed.imported_at
                else:
                    feed.import_attempted_at = timezone.now()
                exception = None
            finally:
                feed.save()

        if exception:
            raise exception
