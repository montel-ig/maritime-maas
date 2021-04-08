import datetime
from decimal import Decimal

import pytest

from gtfs.importers import GTFSFeedImporter
from gtfs.models import Agency, Fare, RiderCategory


@pytest.mark.django_db
def test_gtfs_feed_importer():
    importer = GTFSFeedImporter()
    importer.run("gtfs/tests/data/gtfs_test_feed.zip")

    assert Agency.objects.count() == 1
    agency = Agency.objects.first()
    assert agency.source_id == "ferry_company"
    assert agency.name == "Ferry Company"
    assert agency.url == "https://ferry.company"
    assert agency.timezone == "Europe/Helsinki"

    assert agency.routes.count() == 1
    route = agency.routes.first()
    assert route.source_id == "kauppatori_suomenlinna"
    assert route.short_name == "Suomenlinna"

    assert route.trips.count() == 2
    trip = route.trips.first()
    assert trip.source_id == "1"

    assert trip.stop_times.count() == 2
    stop_time = trip.stop_times.first()
    assert stop_time.arrival_time == datetime.time(10, 0)
    assert stop_time.departure_time == datetime.time(10, 0)
    assert stop_time.stop_sequence == 1

    stop = stop_time.stop
    assert stop.name == "Kauppatori"
    assert stop.point

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
