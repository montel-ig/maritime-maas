import itertools
import json
from datetime import date, timedelta
from uuid import UUID

import pytest
from django.contrib.gis.geos import Point
from model_bakery import baker, seq

from gtfs.models import Departure, Stop, StopTime, Trip
from gtfs.tests.utils import clean_stops_for_snapshot, get_feed_for_maas_operator

ENDPOINT = "/v1/stops/"


@pytest.fixture
def api_id_generator():
    return (UUID(int=i) for i in itertools.count())


@pytest.mark.django_db
def test_stops(maas_api_client, route_with_departures, snapshot):
    response = maas_api_client.get(ENDPOINT)
    assert response.status_code == 200

    content = clean_stops_for_snapshot(json.loads(response.content))
    snapshot.assert_match(content)


@pytest.mark.django_db
def test_stops_with_location_and_radius(maas_api_client):
    point = Point(0.99, 0.99)

    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    baker.make(Stop, feed=feed, point=point)

    response_large_radius = maas_api_client.get(
        f"{ENDPOINT}?location=1.0,1.0&radius=2000"
    )

    response_small_radius = maas_api_client.get(
        f"{ENDPOINT}?location=1.0,1.0&radius=1000"
    )

    assert response_large_radius.status_code == 200
    assert len(json.loads(response_large_radius.content)) == 1

    assert response_small_radius.status_code == 200
    assert len(json.loads(response_small_radius.content)) == 0


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_stops_allowed_for_maas_operator(maas_api_client, has_permission):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, has_permission)
    baker.make(Stop, feed=feed, _quantity=3)

    response = maas_api_client.get(ENDPOINT)

    assert response.status_code == 200

    results_count = len(json.loads(response.content))
    assert results_count == 3 if has_permission else results_count == 0


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
def test_stops_departures(maas_api_client, snapshot, filters, route_with_departures):
    stop = Stop.objects.filter(stop_times__trip__route=route_with_departures).first()

    response = maas_api_client.get(ENDPOINT + f"{stop.api_id}/", filters)

    content = json.loads(response.content)
    if "date" in filters:
        snapshot.assert_match(content["departures"])
    else:
        assert "departures" not in content


@pytest.mark.django_db
def test_stops_departures__stop_appears_multiple_times_in_trip(
    maas_api_client,
    route_for_maas_operator,
    api_id_generator,
    snapshot,
    django_assert_max_num_queries,
):
    """Same stop appears twice (or more) in a trip.

    There is more than one StopTime with the same Stop and Trip, but with different
    arrival and departure times. Stop serializer should return departures with separate
    stop times.
    """
    route = route_for_maas_operator
    feed = route_for_maas_operator.feed

    trip = baker.make(
        Trip,
        route=route,
        feed=feed,
        source_id="source_id of test trip ",
        short_name="short_name of test trip ",
        headsign="headsign of test trip ",
        direction_id=0,
        block_id=seq("block_id of test trip "),
    )
    stops = baker.make(
        Stop,
        feed=feed,
        api_id=api_id_generator,
        name="stop ",
        tts_name="tts_name of stop ",
        code=seq("code of stop"),
        desc="desc of test stop ",
        _quantity=3,
    )
    baker.make(
        StopTime,
        trip=trip,
        stop=iter([stops[0], stops[1], stops[2], stops[1]]),
        feed=feed,
        # -2 hours in Helsinki time
        arrival_time=iter(
            [
                timedelta(hours=8),
                timedelta(hours=9),
                timedelta(hours=10),
                timedelta(hours=11),
            ]
        ),
        # -2 hours in Helsinki time
        departure_time=iter(
            [
                timedelta(hours=9),
                timedelta(hours=10),
                timedelta(hours=11),
                timedelta(hours=12),
            ]
        ),
        stop_headsign="stop_headsign of test stop time ",
        stop_sequence=seq(0),
        timepoint=StopTime.Timepoint.EXACT,
        _quantity=4,
    )
    baker.make(
        Departure,
        api_id=api_id_generator,
        trip=trip,
        date=date(2021, 2, 18),
    )

    with django_assert_max_num_queries(5):
        response = maas_api_client.get(
            ENDPOINT + f"{stops[1].api_id}/", {"date": "2021-02-18"}
        )
    content = response.json()

    snapshot.assert_match(content["departures"])
