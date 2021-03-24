from django.core.management import BaseCommand

from gtfs.importers.gtfs_feed_importer import GTFSFeedImporter


class Command(BaseCommand):
    help = "Imports a GTFS feed."

    def add_arguments(self, parser):
        parser.add_argument("url_or_filename", type=str)
        parser.add_argument("--skip-validation", action="store_true")

    def handle(self, *args, **options):
        importer = GTFSFeedImporter()
        importer.run(options["url_or_filename"], options["skip_validation"])
