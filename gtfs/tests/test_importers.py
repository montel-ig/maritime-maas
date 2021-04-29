import datetime
from decimal import Decimal

import pytest
from django.utils.timezone import localdate

from gtfs.importers import GTFSFeedImporter, GTFSFeedUpdater
from gtfs.models import (
    Agency,
    Fare,
    Feed,
    FeedInfo,
    RiderCategory,
    Route,
    Shape,
    Stop,
    StopTime,
    Trip,
)


@pytest.mark.django_db
def test_gtfs_feed_importer():
    feed = Feed.objects.create(
        name="Test feed", url_or_path="gtfs/tests/data/gtfs_test_feed"
    )
    importer = GTFSFeedImporter()
    importer.run(feed)

    assert feed.fingerprint == datetime.date.today().isoformat()

    assert Agency.objects.count() == 1
    agency = Agency.objects.first()
    assert agency.source_id == "maasline"
    assert agency.name == "MaaS Line Oy"
    assert agency.url == "https://maas.line"
    assert agency.timezone == "Europe/Helsinki"
    assert (
        agency.logo_url
        == "https://cdn.pixabay.com/photo/2013/07/13/10/44/boat-157680_960_720.png"
    )

    assert agency.routes.count() == 1
    route = agency.routes.first()
    assert route.source_id == "vallisaari_rengas"
    assert route.short_name == "vallisaari"
    assert route.long_name == "Vallisaaren reitti"
    route.set_current_language("en")
    assert route.long_name == "Vallisaari Route"
    route.set_current_language("sv")
    assert route.long_name == "Skanslandet rutt"
    assert route.sort_order == 1
    assert route.capacity_sales == Route.CapacitySales.ENABLED

    assert route.trips.count() == 5
    trip = route.trips.first()
    assert trip.source_id == "kauppatori_vallisaari_1"
    assert trip.wheelchair_accessible == Trip.WheelchairAccessible.ACCESSIBLE
    assert trip.bikes_allowed == Trip.BikesAllowed.ALLOWED
    assert trip.block_id == "itäblokki"

    assert trip.stop_times.count() == 2
    stop_time = trip.stop_times.first()
    assert stop_time.arrival_time == datetime.timedelta(hours=8)
    assert stop_time.departure_time == datetime.timedelta(hours=8)
    assert stop_time.stop_sequence == 1
    assert stop_time.timepoint == StopTime.Timepoint.EXACT
    stop_time_2 = trip.stop_times.last()
    assert stop_time_2.arrival_time == datetime.timedelta(hours=24)
    assert stop_time_2.departure_time == datetime.timedelta(hours=25, minutes=30)
    assert stop_time_2.stop_sequence == 2
    assert stop_time_2.timepoint == StopTime.Timepoint.APPROXIMATE

    stop = stop_time.stop
    assert stop.name == "Kauppatori - Lyypekinlaituri"
    assert stop.point
    assert stop.tts_name == "Kauppatori"
    assert stop.wheelchair_boarding == Stop.WheelchairBoarding.POSSIBLE

    assert route.fare_rules.count() == 1
    fare_rule = route.fare_rules.first()

    fare = fare_rule.fare
    assert fare.price == Decimal("5.5")
    assert fare.currency_type == "EUR"
    assert fare.payment_method == Fare.PaymentMethod.BEFORE_BOARDING
    assert fare.transfers == Fare.Transfers.TWO_TRANSFERS
    assert fare.name == "Matkalippu"
    assert fare.description == "Lippu vallisaareen ja rengasreitille"
    assert fare.instructions == "Esitä lippu, kun astut alukseen."

    assert fare.fare_rider_categories.count() == 3
    fare_rider_category = fare.fare_rider_categories.first()
    assert fare_rider_category.price == Decimal("4.5")
    assert fare_rider_category.currency_type == "EUR"

    assert RiderCategory.objects.count() == 3
    rider_category = RiderCategory.objects.first()
    assert rider_category.source_id == "pensioner"
    assert rider_category.name == "Eläkeläinen"
    assert rider_category.description == "Eläkeläinen"

    assert FeedInfo.objects.count() == 1
    feed_info = FeedInfo.objects.first()
    assert feed_info.feed == feed
    assert feed_info.publisher_name == "Lipunmyynti Oy"
    assert feed_info.publisher_url == "https://lipunmyyn.ti"
    assert feed_info.lang == "fi"
    assert feed_info.default_lang == "en"
    assert feed_info.start_date == datetime.date(2021, 1, 1)
    assert feed_info.end_date == datetime.date(2021, 12, 31)
    assert feed_info.version == "1"
    assert feed_info.contact_email == "feed_contact@example.com"

    assert Shape.objects.count() == 3
    assert len(trip.shape.geometry) == 9


@pytest.mark.django_db
def test_feed_updater():
    feed = Feed.objects.create(url_or_path="gtfs/tests/data/gtfs_test_feed")
    assert feed.last_import_successful is None
    importer = GTFSFeedUpdater()
    importer.update_feeds()

    feed.refresh_from_db()
    assert feed.fingerprint == localdate().isoformat()
    assert Agency.objects.count() == 1
    # success so imported_at should be the same as import_attempted_at
    assert feed.imported_at and feed.imported_at == feed.import_attempted_at
    assert feed.last_import_successful

    feed.url_or_path = "failure-path"
    feed.fingerprint = ""
    feed.save()
    importer.update_feeds()

    feed.refresh_from_db()
    # failure, so import_attempted_at should be after imported_at
    assert feed.import_attempted_at > feed.imported_at
    assert feed.last_import_successful is False

    # test one more success to verify functioning after a failure
    feed.url_or_path = "gtfs/tests/data/gtfs_test_feed"
    feed.fingerprint = ""
    feed.save()
    importer.update_feeds()

    feed.refresh_from_db()
    assert feed.imported_at and feed.imported_at == feed.import_attempted_at
    assert feed.last_import_successful
