import datetime
from decimal import Decimal

import pytest

from gtfs.importers import GTFSFeedImporter
from gtfs.models import Agency, Fare, RiderCategory, Stop, StopTime, Trip


@pytest.mark.django_db
def test_gtfs_feed_importer():
    importer = GTFSFeedImporter()
    importer.run("gtfs/tests/data/gtfs_test_feed.zip")

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
    assert route.sort_order == 1

    assert route.trips.count() == 5
    trip = route.trips.first()
    assert trip.source_id == "kauppatori_vallisaari_1"
    assert trip.wheelchair_accessible == Trip.WheelchairAccessible.ACCESSIBLE
    assert trip.bikes_allowed == Trip.BikesAllowed.ALLOWED
    assert trip.capacity_sales == Trip.CapacitySales.REQUIRED

    assert trip.stop_times.count() == 2
    stop_time = trip.stop_times.first()
    assert stop_time.arrival_time == datetime.time(8, 0)
    assert stop_time.departure_time == datetime.time(8, 0)
    assert stop_time.stop_sequence == 1
    assert stop_time.timepoint == StopTime.Timepoint.EXACT

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

    assert fare.fare_rider_categories.count() == 3
    fare_rider_category = fare.fare_rider_categories.first()
    assert fare_rider_category.price == Decimal("4.5")
    assert fare_rider_category.currency_type == "EUR"

    assert RiderCategory.objects.count() == 3
    rider_category = RiderCategory.objects.first()
    assert rider_category.source_id == "pensioner"
    assert rider_category.name == "Eläkeläinen"
    assert rider_category.description == "Eläkeläinen"
