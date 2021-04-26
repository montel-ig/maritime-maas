import itertools
import json
from uuid import UUID

import pytest
from model_bakery import baker

from gtfs.models import Departure, Route, Shape, Trip
from gtfs.tests.utils import clean_shapes_for_snapshot, get_feed_for_maas_operator

ENDPOINT = "/v1/shapes/"


@pytest.fixture
def api_id_generator():
    return (UUID(int=i) for i in itertools.count())


@pytest.mark.parametrize(
    "filtering",
    [
        {},
        {"route_id": "00000000-0000-0000-0000-000000000000"},
        {"route_id": "00000000-0000-0000-0000-000000000001"},
        {"departure_id": "00000000-0000-0000-0000-000000000002"},  # first route
        {"departure_id": "00000000-0000-0000-0000-000000000004"},  # second route
    ],
)
@pytest.mark.django_db
def test_shapes(maas_api_client, snapshot, api_id_generator, filtering):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    routes = baker.make(Route, feed=feed, api_id=api_id_generator, _quantity=2)
    shapes = baker.make(
        Shape,
        api_id=iter(
            [
                "DEADBEEF-0000-0000-0000-000000000000",  # first route
                "BABEFACE-0000-0000-0000-000000000000",  # first route
                "C0FFEE00-0000-0000-0000-000000000000",  # second route
            ]
        ),
        feed=feed,
        _quantity=3,
    )

    first_route_trips = baker.make(
        Trip,
        feed=feed,
        route=routes[0],
        shape=iter([shapes[0], shapes[1]]),
        _quantity=2,
    )
    second_route_trip = baker.make(Trip, feed=feed, route=routes[1], shape=shapes[2])
    baker.make(
        Departure,
        api_id=api_id_generator,
        trip=iter([first_route_trips[0], first_route_trips[1], second_route_trip]),
        _quantity=3,
    )

    response = maas_api_client.get(ENDPOINT, filtering)
    content = json.loads(response.content)
    if filtering:
        assert response.status_code == 200
        content = clean_shapes_for_snapshot(content)
    else:
        assert response.status_code == 400
    snapshot.assert_match(content)
