import json

import pytest
from django.contrib.gis.geos import Point
from model_bakery import baker

from gtfs.models import Stop


@pytest.mark.django_db
def test_stops(api_client):
    endpoint = "/v1/stops/"

    baker.make(Stop, _quantity=3)

    response = api_client().get(endpoint)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 3


@pytest.mark.django_db
def test_stops_with_location_and_radius(api_client):
    endpoint = "/v1/stops/"

    point = Point(0.99, 0.99)

    baker.make(Stop, point=point)

    response_large_radius = api_client().get(f"{endpoint}?location=1.0,1.0&radius=2000")

    response_small_radius = api_client().get(f"{endpoint}?location=1.0,1.0&radius=1000")

    assert response_large_radius.status_code == 200
    assert len(json.loads(response_large_radius.content)) == 1

    assert response_small_radius.status_code == 200
    assert len(json.loads(response_small_radius.content)) == 0
