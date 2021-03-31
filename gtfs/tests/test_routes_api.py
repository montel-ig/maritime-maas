import json

import pytest
from model_bakery import baker

from gtfs.models import Route, Stop, StopTime, Trip
from gtfs.tests.utils import get_feed_for_maas_operator


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
