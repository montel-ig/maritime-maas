import json

import pytest
from django.contrib.gis.geos import Point
from model_bakery import baker

from gtfs.models import Stop
from gtfs.tests.utils import get_feed_for_maas_operator


@pytest.mark.django_db
def test_stops(maas_api_client):
    endpoint = "/v1/stops/"

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    baker.make(Stop, feed=feed, _quantity=3)

    response = maas_api_client.get(endpoint)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 3


@pytest.mark.django_db
def test_stops_with_location_and_radius(maas_api_client):
    endpoint = "/v1/stops/"

    point = Point(0.99, 0.99)

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    baker.make(Stop, feed=feed, point=point)

    response_large_radius = maas_api_client.get(
        f"{endpoint}?location=1.0,1.0&radius=2000"
    )

    response_small_radius = maas_api_client.get(
        f"{endpoint}?location=1.0,1.0&radius=1000"
    )

    assert response_large_radius.status_code == 200
    assert len(json.loads(response_large_radius.content)) == 1

    assert response_small_radius.status_code == 200
    assert len(json.loads(response_small_radius.content)) == 0


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_stops_allowed_for_maas_operator(maas_api_client, has_permission):

    endpoint = "/v1/stops/"

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, has_permission)
    baker.make(Stop, feed=feed, _quantity=3)

    response = maas_api_client.get(endpoint)

    assert response.status_code == 200

    results_count = len(json.loads(response.content))
    assert results_count == 3 if has_permission else results_count == 0
