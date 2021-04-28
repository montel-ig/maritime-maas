import json

import pytest
from model_bakery import baker, seq

from gtfs.models import (
    Fare,
    FareRiderCategory,
    FareRule,
    RiderCategory,
    Route,
    Stop,
    StopTime,
    Trip,
)
from gtfs.tests.utils import clean_stops_for_snapshot, get_feed_for_maas_operator

ENDPOINT = "/v1/routes/"


@pytest.mark.django_db
def test_routes(maas_api_client, route_with_departures, snapshot):
    response = maas_api_client.get(ENDPOINT)
    assert response.status_code == 200

    content = json.loads(response.content)

    for route in content:
        route["stops"] = clean_stops_for_snapshot(route["stops"])

    snapshot.assert_match(content)


@pytest.mark.django_db
def test_routes_with_stop_id(maas_api_client):

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    routes = baker.make(Route, feed=feed, _quantity=3)
    trip = baker.make(Trip, route=routes[0], feed=feed)
    stop = baker.make(Stop, feed=feed)
    baker.make(StopTime, trip=trip, stop=stop, feed=feed)

    url = f"{ENDPOINT}?stop_id={stop.api_id}"

    response = maas_api_client.get(url)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 1


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_routes_allowed_for_maas_operator(maas_api_client, has_permission):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, has_permission)
    route = baker.make(Route, feed=feed)
    trip = baker.make(Trip, route=route, feed=feed)
    stop = baker.make(Stop, feed=feed)
    baker.make(StopTime, trip=trip, stop=stop, feed=feed)

    response = maas_api_client.get(ENDPOINT)

    results_count = len(json.loads(response.content))
    assert response.status_code == 200
    assert results_count == 1 if has_permission else results_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filters",
    (
        {},
        {"direction_id": 0},
        {"date": "2021-02-18"},
        {"date": "2021-02-19"},
        {"date": "2021-02-18", "direction_id": 0},
        {"date": "2021-02-18", "direction_id": 1},
        {"date": "2021-02-20"},
    ),
)
def test_routes_departures(maas_api_client, snapshot, filters, route_with_departures):
    response = maas_api_client.get(
        ENDPOINT + f"{route_with_departures.api_id}/", filters
    )

    for stop_content in json.loads(response.content)["stops"]:
        if "date" in filters:
            # REMARK: even when there is a single date filter, snapshots of a single
            # test can still include arrival_time and departure_time datetimes of
            # multiple days, because we want GTFS times that go past midnight
            # (like 26:00) to be still tied to the date of their departure
            snapshot.assert_match(stop_content["departures"])
        else:
            assert "departures" not in stop_content


@pytest.mark.django_db
def test_route_ordering(maas_api_client):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    baker.make(
        Route,
        feed=feed,
        short_name=iter(["third", "first", "second"]),
        sort_order=iter([3, 1, 2]),
        _quantity=3,
    )

    response = maas_api_client.get(ENDPOINT)
    assert response.status_code == 200
    assert [r["name"] for r in response.data] == ["first", "second", "third"]


@pytest.mark.django_db
def test_rider_categories_with_prices(
    maas_api_client, snapshot, api_id_generator, django_assert_max_num_queries
):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    route = baker.make(Route, feed=feed)
    fare = baker.make(
        Fare,
        feed=feed,
        source_id=seq("source_id of test fare "),
        api_id=api_id_generator,
        name="Name",
        description="Description",
        instructions="Instructions",
    )
    baker.make(FareRule, feed=feed, fare=fare, route=route)
    rider_categories = baker.make(
        RiderCategory,
        feed=feed,
        api_id=api_id_generator,
        source_id=seq("source_id of test rider category "),
        name=seq("name of test rider category "),
        description=seq("description of test rider category "),
        _quantity=3,
    )
    baker.make(
        FareRiderCategory,
        feed=feed,
        fare=fare,
        rider_category=iter(rider_categories),
        currency_type="EUR",
        price=seq(0),
        _quantity=len(rider_categories),
    )

    with django_assert_max_num_queries(7):
        response = maas_api_client.get(ENDPOINT)
    response_content = json.loads(response.content)

    assert len(response_content) == 1
    ticket_types = response_content[0]["ticket_types"]
    snapshot.assert_match(ticket_types)
