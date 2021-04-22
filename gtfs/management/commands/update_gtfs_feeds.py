from django.core.management import BaseCommand

from gtfs.importers import GTFSFeedUpdater


class Command(BaseCommand):
    help = "Update existing GTFS feeds."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update all existing feeds by not checking if they've really been updated.",
        )

    def handle(self, *args, **options):
        updater = GTFSFeedUpdater()
        updater.update_feeds(force=options["force"])
