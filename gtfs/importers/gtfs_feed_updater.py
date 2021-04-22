import logging

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

    def update_single_feed(self, feed: Feed, force: bool = False):
        fingerprint = self.reader.get_feed_fingerprint(feed)
        if fingerprint != feed.fingerprint or force:
            self.importer.run(feed.name)
        else:
            self.logger.info(
                f'No need to update feed "{feed.name}", same fingerprint: "{feed.fingerprint}"'
            )
