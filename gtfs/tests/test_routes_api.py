import json

import pytest
from model_bakery import baker

from gtfs.models import Route, Stop, StopTime, Trip
from gtfs.tests.utils import get_feed_for_maas_operator

ENDPOINT = "/v1/routes/"


@pytest.mark.django_db
def test_routes(maas_api_client):
    endpoint = "/v1/routes/"

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    route = baker.make(Route, feed=feed)
    trip = baker.make(Trip, route=route, feed=feed)
    stop = baker.make(Stop, feed=feed)
    baker.make(StopTime, trip=trip, stop=stop, feed=feed)

    response = maas_api_client.get(endpoint)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 1


@pytest.mark.django_db
def test_routes_with_stop_id(maas_api_client):

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    routes = baker.make(Route, feed=feed, _quantity=3)
    trip = baker.make(Trip, route=routes[0], feed=feed)
    stop = baker.make(Stop, feed=feed)
    baker.make(StopTime, trip=trip, stop=stop, feed=feed)

    endpoint = "/v1/routes/"
    url = f"{endpoint}?stop_id={stop.api_id}"

    response = maas_api_client.get(url)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 1


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_routes_allowed_for_maas_operator(maas_api_client, has_permission):
    endpoint = "/v1/routes/"

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, has_permission)
    route = baker.make(Route, feed=feed)
    trip = baker.make(Trip, route=route, feed=feed)
    stop = baker.make(Stop, feed=feed)
    baker.make(StopTime, trip=trip, stop=stop, feed=feed)

    response = maas_api_client.get(endpoint)

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
            snapshot.assert_match(stop_content["departures"])
        else:
            assert "departures" not in stop_content
