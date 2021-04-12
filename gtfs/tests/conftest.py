import itertools
from datetime import date, time, timedelta
from uuid import UUID

import pytest
from model_bakery import baker, seq
from rest_framework.test import APIClient

from gtfs.models import Agency, Departure, Route, Stop, StopTime, Trip
from gtfs.tests.utils import get_feed_for_maas_operator
from maas.models import MaasOperator
from maas.tests.utils import token_authenticate


@pytest.fixture
def maas_operator():
    return baker.make(MaasOperator)


@pytest.fixture
def maas_api_client(maas_operator):
    api_client = APIClient()
    token_authenticate(api_client, maas_operator.user)
    api_client.maas_operator = maas_operator
    return api_client


@pytest.fixture
def api_id_generator():
    return (UUID(int=i) for i in itertools.count())


@pytest.fixture
def route_with_departures(maas_operator, api_id_generator):
    """
    A route with
        * 2 trips each having 2 stops and 2 stop times
        * 3 departures (first trip having two departures on separate days)
    """
    feed = get_feed_for_maas_operator(maas_operator, True)

    agency = baker.make(
        Agency,
        feed=feed,
        name="test agency",
        url="www.testagency.com",
        logo_url="www.testagency.com/logo",
    )

    route = baker.make(Route, feed=feed, api_id=api_id_generator, agency=agency)
    trips = baker.make(
        Trip,
        route=route,
        feed=feed,
        source_id=seq("source_id of test trip "),
        short_name=seq("short_name of test trip "),
        headsign=seq("headsign of test trip "),
        direction_id=itertools.cycle([0, 1]),
        _quantity=2,
    )

    stops = baker.make(
        Stop,
        feed=feed,
        api_id=api_id_generator,
        name=seq("stop "),
        tts_name=seq("tts_name of stop "),
        code=seq("code of stop"),
        _quantity=2,
    )
    for i, trip in enumerate(trips):
        baker.make(
            StopTime,
            trip=trip,
            stop=iter(stops),
            feed=feed,
            arrival_time=seq(time(12, i * 15), timedelta(hours=1)),
            departure_time=seq(time(12, i * 15), timedelta(hours=1)),
            stop_headsign=seq("stop_headsign of test stop time ", start=i * 2),
            stop_sequence=seq(0),
            _quantity=2,
        )

    departures = baker.make(
        Departure,
        api_id=api_id_generator,
        trip=iter(trips),
        date=date(2021, 2, 18),
        _quantity=2,
    )
    departures.append(
        baker.make(
            Departure,
            api_id=api_id_generator,
            trip=trips[0],
            date=date(2021, 2, 19),
        )
    )

    return route
