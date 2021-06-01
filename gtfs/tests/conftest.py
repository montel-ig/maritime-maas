import itertools
from datetime import date, timedelta
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
    return baker.make(
        MaasOperator,
        name=seq("name of maas operator "),
        identifier=seq("identifier of maas operator "),
    )


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
def route_for_maas_operator(maas_operator, api_id_generator):
    feed = get_feed_for_maas_operator(maas_operator, True)

    agency = baker.make(
        Agency,
        feed=feed,
        name="test agency",
        url="www.testagency.com",
        logo_url="www.testagency.com/logo",
        timezone="Europe/Helsinki",
        email="test-agency@example.com",
        phone="777777",
    )

    route = baker.make(
        Route,
        feed=feed,
        api_id=api_id_generator,
        agency=agency,
        desc="desc of test route ",
        url="url of test route ",
        capacity_sales=Route.CapacitySales.DISABLED,
    )

    return route


@pytest.fixture
def route_with_departures(api_id_generator, route_for_maas_operator):
    """
    A route with
        * 2 trips each having 2 stops and 2 stop times
        * 3 departures (first trip having two departures on separate days)
    """
    route = route_for_maas_operator
    feed = route_for_maas_operator.feed

    trips = baker.make(
        Trip,
        route=route,
        feed=feed,
        source_id="source_id of test trip ",
        short_name="short_name of test trip ",
        headsign="headsign of test trip ",
        direction_id=itertools.cycle([0, 1]),
        block_id=seq("block_id of test trip "),
        _quantity=2,
    )

    stops = baker.make(
        Stop,
        feed=feed,
        api_id=api_id_generator,
        name="stop ",
        tts_name="tts_name of stop ",
        code=seq("code of stop"),
        desc="desc of test stop ",
        _quantity=2,
    )
    for i, trip in enumerate(trips):
        baker.make(
            StopTime,
            trip=trip,
            stop=iter(stops),
            feed=feed,
            # 13:00, 13:15, 00:00, 00:15 in Helsinki time
            arrival_time=iter(
                [
                    timedelta(hours=15, minutes=i * 15),
                    timedelta(hours=26, minutes=i * 15),
                ]
            ),
            # 13:00, 13:15, 01:00, 01:15 in Helsinki time
            departure_time=iter(
                [
                    timedelta(hours=15, minutes=i * 15),
                    timedelta(hours=27, minutes=i * 15),
                ]
            ),
            stop_headsign="stop_headsign of test stop time ",
            stop_sequence=seq(0),
            timepoint=StopTime.Timepoint.EXACT,
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
