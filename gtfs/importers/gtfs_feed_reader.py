import csv
import hashlib
import shutil
import tempfile
from collections import namedtuple
from pathlib import Path
from typing import List, Union

import gtfs_kit
import requests
from django.utils.timezone import localdate
from requests import RequestException
from rest_framework import serializers

from gtfs.models import Feed


class RiderCategorySerializer(serializers.Serializer):
    rider_category_id = serializers.CharField()
    rider_category_name = serializers.CharField(max_length=255)
    rider_category_description = serializers.CharField(max_length=255)


class FareRiderCategorySerializer(serializers.Serializer):
    fare_id = serializers.CharField()
    rider_category_id = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency_type = serializers.CharField(max_length=3)


class GTFSFeedReader:

    EXTRA_FILES = {
        "rider_categories": RiderCategorySerializer,
        "fare_rider_categories": FareRiderCategorySerializer,
    }

    def read_feed(self, url_or_filename):
        feed = gtfs_kit.read_feed(url_or_filename, dist_units="km")

        extra_data = self._read_feed_extra(url_or_filename)
        for key, value in extra_data.items():
            setattr(feed, key, value)

        return feed

    def validate(self, gtfs_feed) -> List:
        problems = gtfs_kit.validate(gtfs_feed, as_df=False)

        for dataset_file, serializer in self.EXTRA_FILES.items():
            if dataset := getattr(gtfs_feed, dataset_file, None):
                for row_index, row_data in enumerate(dataset, 1):
                    validator = serializer(data=row_data._asdict())
                    if not validator.is_valid():
                        problems.append(
                            ["error", validator.errors, dataset_file, row_index]
                        )

        return problems

    def _read_feed_extra(self, path_or_url: Union[Path, str]):
        """Read GTFS extra data

        This helper will read defined extra data from files which are ignored
        by gtfs_kit.
        """
        try:
            path_exists = Path(path_or_url).exists()
        except OSError:
            path_exists = False
        if path_exists:
            return self._read_feed_extra_from_path(path_or_url)
        elif requests.head(path_or_url).ok:
            return self._read_feed_extra_from_url(path_or_url)
        else:
            raise ValueError("Path does not exist or URL has bad status.")

    def _read_feed_extra_from_path(self, path: Union[Path, str]):
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Path {path} does not exist")

        # Unzip path to temporary directory if necessary
        if path.is_file():
            zipped = True
            tmp_dir = tempfile.TemporaryDirectory()
            src_path = Path(tmp_dir.name)
            shutil.unpack_archive(str(path), tmp_dir.name, "zip")
        else:
            zipped = False
            src_path = path

        feed_extra_dict = {key: None for key in self.EXTRA_FILES}
        for p in src_path.iterdir():
            dataset_file = p.stem
            # Skip empty files, irrelevant files, and files with no data
            if (
                p.is_file()
                and p.stat().st_size
                and p.suffix == ".txt"
                and dataset_file in self.EXTRA_FILES
            ):
                with open(p, newline="") as csvfile:
                    csv_reader = csv.reader(csvfile)
                    headers = next(csv_reader)
                    GtfsRow = namedtuple(dataset_file, headers)
                    feed_extra_dict[dataset_file] = list(map(GtfsRow._make, csv_reader))

        # Delete temporary directory
        if zipped:
            tmp_dir.cleanup()

        return feed_extra_dict

    def _read_feed_extra_from_url(self, url: str):
        f = tempfile.NamedTemporaryFile(delete=False)
        with requests.get(url) as r:
            f.write(r._content)
        f.close()
        feed = self._read_feed_extra_from_path(f.name)
        Path(f.name).unlink()
        return feed

    def get_feed_fingerprint(self, feed: Feed) -> str:
        """Return a fingerprint for the feed.

        Fingerprint can be used to check if the feed has changed and needs to
        be updated.

        Logic will return the first item on the following list:
        - HTTP last-modified header
        - sha1 hash of the zip file
        - date of last import (fallback to import once per day)
        """
        fingerprint = None

        try:
            response = requests.head(feed.name)
            response.raise_for_status()
            if timestamp := response.headers.get("last-modified"):
                fingerprint = timestamp

            if not fingerprint:
                response = requests.get(feed.name)
                response.raise_for_status()
                sha1 = hashlib.sha1()
                sha1.update(response.content)
                fingerprint = sha1.hexdigest()
        except RequestException:
            fingerprint = localdate().isoformat()

        return fingerprint[:255]
