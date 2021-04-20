import json
from dataclasses import dataclass
from typing import List

import pytest
from model_bakery import baker, seq

from bookings.models import Booking
from gtfs.models import (
    Departure,
    Fare,
    FareRiderCategory,
    FareRule,
    Feed,
    RiderCategory,
    Route,
)
from gtfs.tests.utils import get_feed_for_maas_operator
from maas.models import MaasOperator

ENDPOINT = "/v1/bookings/"


@dataclass
class TestData:
    feed: Feed
    routes: List[Route]
    fares: List[Fare]
    rider_categories: List[RiderCategory]
    departures: List[Departure]


@pytest.fixture
def fare_test_data(maas_operator, api_id_generator):
    """Basically two routes, two fares, two rider_categories and two departures."""
    feed = get_feed_for_maas_operator(maas_operator, True)
    routes = baker.make(Route, feed=feed, _quantity=2)
    fares = baker.make(
        Fare,
        feed=feed,
        source_id=seq("source_id of test fare "),
        api_id=api_id_generator,
        name=seq("Name of test fare "),
        description=seq("Description of test fare "),
        instructions=seq("Instructions of test fare "),
        _quantity=2,
    )

    baker.make(FareRule, feed=feed, fare=iter(fares), route=iter(routes))
    rider_categories = baker.make(
        RiderCategory,
        feed=feed,
        source_id=seq("source_id of test rider category "),
        api_id=api_id_generator,
        name=seq("name of test rider category "),
        description=seq("description of test rider category "),
        _quantity=2,
    )
    baker.make(
        FareRiderCategory,
        feed=feed,
        fare=iter(fares),
        rider_category=iter(rider_categories),
        currency_type="EUR",
        price=seq(1),
        _quantity=2,
    )
    departures = baker.make(
        Departure,
        trip__feed=feed,
        api_id=api_id_generator,
        trip__route=iter(routes),
        _quantity=2,
    )

    return TestData(
        feed,
        routes,
        fares,
        rider_categories,
        departures,
    )


@pytest.mark.django_db
@pytest.mark.parametrize("has_route", [True, False])
def test_create_booking(maas_api_client, has_route, fare_test_data):
    post_data = {
        "departure_ids": [fare_test_data.departures[0].api_id],
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[0].api_id,
                "ticket_type_id": fare_test_data.fares[0].api_id,
            }
        ],
    }
    if has_route:
        post_data["route_id"] = fare_test_data.routes[0].api_id

    response = maas_api_client.post(ENDPOINT, post_data)

    assert response.status_code == 201
    assert {"id", "status"} == set(response.data.keys())
    assert Booking.objects.count() == 1
    assert Booking.objects.first().status == Booking.Status.RESERVED


@pytest.mark.django_db
def test_create_booking_no_permission(maas_api_client, fare_test_data, snapshot):
    data = {
        "route": fare_test_data.routes[0].api_id,
        "departure_ids": [fare_test_data.departures[0].api_id],
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[0].api_id,
                "ticket_type_id": fare_test_data.fares[0].api_id,
            }
        ],
    }
    maas_api_client.maas_operator.permissions.all().delete()

    response = maas_api_client.post(ENDPOINT, data)

    assert response.status_code == 400
    snapshot.assert_match(json.loads(response.content))


@pytest.mark.parametrize("rider_category_index,fare_index", [(0, 1), (1, 0), (1, 1)])
@pytest.mark.django_db
def test_create_booking_illegal_rider_category_or_fare(
    maas_api_client,
    snapshot,
    rider_category_index,
    fare_index,
    fare_test_data,
):
    post_data = {
        "route_id": fare_test_data.routes[0].api_id,
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[
                    rider_category_index
                ].api_id,
                "ticket_type_id": fare_test_data.fares[fare_index].api_id,
            }
        ],
    }

    response = maas_api_client.post(ENDPOINT, post_data)

    assert response.status_code == 400
    snapshot.assert_match(json.loads(response.content))


@pytest.mark.parametrize(
    "has_route,departure_indices", [(True, [1]), (True, [0, 1]), (False, [0, 1])]
)
@pytest.mark.django_db
def test_create_booking_illegal_departures(
    maas_api_client,
    snapshot,
    has_route,
    departure_indices,
    fare_test_data,
):
    post_data = {
        "departure_ids": [
            fare_test_data.departures[i].api_id for i in departure_indices
        ],
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[0].api_id,
                "ticket_type_id": fare_test_data.fares[0].api_id,
            }
        ],
    }
    if has_route:
        post_data["route_id"] = fare_test_data.routes[0].api_id

    response = maas_api_client.post(ENDPOINT, post_data)

    assert response.status_code == 400
    snapshot.assert_match(json.loads(response.content))


@pytest.mark.django_db
def test_confirm_booking(maas_api_client):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    reserved_booking = baker.make(
        Booking,
        maas_operator=maas_api_client.maas_operator,
        ticketing_system=feed.ticketing_system,
    )

    response = maas_api_client.post(f"{ENDPOINT}{reserved_booking.api_id}/confirm/")

    assert response.status_code == 200
    assert {"id", "status"} == set(response.data.keys())
    assert Booking.objects.count() == 1
    assert Booking.objects.first().status == Booking.Status.CONFIRMED


@pytest.mark.django_db
def test_confirm_booking_not_own(maas_api_client):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    another_maas_operator = baker.make(MaasOperator)
    reserved_booking = baker.make(
        Booking,
        maas_operator=another_maas_operator,
        ticketing_system=feed.ticketing_system,
    )

    response = maas_api_client.post(f"{ENDPOINT}{reserved_booking.api_id}/confirm/")

    assert response.status_code == 404
    assert Booking.objects.count() == 1
    assert Booking.objects.first().status == Booking.Status.RESERVED
