import datetime
import json
import uuid
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time
from model_bakery import baker, seq
from rest_framework import status

from bookings.models import Booking
from gtfs.models import Departure, Route
from gtfs.tests.utils import get_feed_for_maas_operator
from maas.models import MaasOperator
from mock_ticket_api.utils import get_confirmations_data, get_reservation_data

ENDPOINT = "/v1/bookings/"


@pytest.fixture
def booking_post_data(fare_test_data):
    return {
        "transaction_id": "transactionID",
        "departure_ids": [fare_test_data.departures[0].api_id],
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[0].api_id,
                "ticket_type_id": fare_test_data.fares[0].api_id,
            }
        ],
    }


@pytest.mark.django_db
@pytest.mark.parametrize("has_route", [True, False])
def test_create_booking(
    maas_api_client, has_route, booking_post_data, fare_test_data, requests_mock
):
    ticketing_system = fare_test_data.feed.ticketing_system
    requests_mock.post(
        ticketing_system.bookings_api_url,
        json=get_reservation_data(),
        status_code=status.HTTP_201_CREATED,
    )
    if has_route:
        booking_post_data["route_id"] = fare_test_data.routes[0].api_id

    response = maas_api_client.post(ENDPOINT, booking_post_data)

    assert response.status_code == 201
    assert set(response.data.keys()) == {"id", "status"}
    assert Booking.objects.count() == 1
    booking = Booking.objects.first()
    assert booking.status == Booking.Status.RESERVED
    assert booking.transaction_id == "transactionID"
    assert booking.ticket_count == 1
    assert booking.route_name == fare_test_data.routes[0].long_name


@pytest.mark.django_db
def test_create_booking_passes_extra_parameters(
    maas_api_client, fare_test_data, requests_mock
):
    ticketing_system = fare_test_data.feed.ticketing_system
    requests_mock.post(
        ticketing_system.bookings_api_url,
        json=get_reservation_data(),
        status_code=status.HTTP_201_CREATED,
    )
    extra_params = {
        "request_id": "requestID",
        "transaction_id": "transactionID",
        "locale": "sv",
    }
    post_data = {
        "route_id": fare_test_data.routes[0].api_id,
        "departure_ids": [fare_test_data.departures[0].api_id],
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[0].api_id,
                "ticket_type_id": fare_test_data.fares[0].api_id,
            }
        ],
        **extra_params,
    }

    maas_api_client.post(ENDPOINT, post_data)

    assert requests_mock.call_count == 1
    request_data = requests_mock.request_history[0].json()
    for key, value in extra_params.items():
        assert request_data[key] == value


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


@pytest.mark.parametrize(
    "capacity_sales,direction_ids,valid",
    [
        (Route.CapacitySales.REQUIRED_FOR_OUTBOUND, [0], True),
        (Route.CapacitySales.REQUIRED_FOR_INBOUND, [1], True),
        (Route.CapacitySales.REQUIRED_FOR_OUTBOUND, [1], False),
        (Route.CapacitySales.REQUIRED_FOR_INBOUND, [0], False),
        (Route.CapacitySales.REQUIRED_FOR_OUTBOUND, [0, 0], False),
        (Route.CapacitySales.REQUIRED_FOR_OUTBOUND, [None], False),
    ],
)
@pytest.mark.django_db
def test_create_booking_capacity_sales_required_for_outbound_and_inbound(
    maas_api_client,
    snapshot,
    fare_test_data,
    capacity_sales,
    direction_ids,
    valid,
    api_id_generator,
    requests_mock,
):
    requests_mock.post(
        fare_test_data.feed.ticketing_system.bookings_api_url,
        json=get_reservation_data(),
        status_code=status.HTTP_201_CREATED,
    )
    route = fare_test_data.routes[0]
    route.capacity_sales = capacity_sales
    route.save()

    departures = [
        baker.make(
            Departure,
            trip__feed=fare_test_data.feed,
            trip__source_id=seq("source_id of trip "),
            trip__direction_id=d_id,
            api_id=api_id_generator,
            date=datetime.date(2021, 4, 28),
            trip__route=fare_test_data.routes[0],
        )
        for d_id in direction_ids
    ]

    post_data = {
        "route_id": route.api_id,
        "departure_ids": [d.api_id for d in departures],
        "tickets": [
            {
                "customer_type_id": fare_test_data.rider_categories[0].api_id,
                "ticket_type_id": fare_test_data.fares[0].api_id,
            }
        ],
    }

    response = maas_api_client.post(ENDPOINT, post_data)

    if valid:
        assert response.status_code == 201
    else:
        snapshot.assert_match(json.loads(response.content))
        assert response.status_code == 400


@pytest.mark.django_db
@freeze_time("2021-04-20")
@pytest.mark.parametrize("source_id_changes", [True, False])
def test_confirm_booking(maas_api_client, requests_mock, snapshot, source_id_changes):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    reserved_booking = baker.make(
        Booking,
        maas_operator=maas_api_client.maas_operator,
        ticketing_system=feed.ticketing_system,
    )
    ticketing_system = feed.ticketing_system
    expected_source_id = (
        str(uuid.uuid4()) if source_id_changes else reserved_booking.source_id
    )
    requests_mock.post(
        urljoin(
            ticketing_system.bookings_api_url, f"{reserved_booking.source_id}/confirm/"
        ),
        json=get_confirmations_data(expected_source_id, include_qr=False),
        status_code=status.HTTP_200_OK,
    )

    response = maas_api_client.post(
        f"{ENDPOINT}{reserved_booking.api_id}/confirm/",
        {
            "transaction_id": "transactionID",
        },
    )

    assert response.status_code == 200
    assert set(response.data.keys()) == {"id", "status", "tickets"}
    snapshot.assert_match(response.data["tickets"])
    assert Booking.objects.count() == 1
    reserved_booking.refresh_from_db()
    assert reserved_booking.status == Booking.Status.CONFIRMED
    assert reserved_booking.source_id == expected_source_id
    assert reserved_booking.transaction_id == "transactionID"


@pytest.mark.django_db
def test_confirm_booking_passes_extra_parameters(maas_api_client, requests_mock):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    extra_params = {
        "request_id": "requestID",
        "transaction_id": "transactionID",
        "locale": "sv",
    }
    reserved_booking = baker.make(
        Booking,
        maas_operator=maas_api_client.maas_operator,
        ticketing_system=feed.ticketing_system,
    )
    ticketing_system = feed.ticketing_system
    requests_mock.post(
        urljoin(
            ticketing_system.bookings_api_url, f"{reserved_booking.source_id}/confirm/"
        ),
        json=get_confirmations_data(reserved_booking.source_id, include_qr=False),
        status_code=status.HTTP_200_OK,
    )

    maas_api_client.post(f"{ENDPOINT}{reserved_booking.api_id}/confirm/", extra_params)

    assert requests_mock.call_count == 1
    request_data = requests_mock.request_history[0].json()
    for key, value in extra_params.items():
        assert request_data[key] == value


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


@pytest.mark.django_db
@freeze_time("2021-04-20")
def test_retrieve_confirmed_booking(maas_api_client, requests_mock, snapshot):
    feed = get_feed_for_maas_operator(maas_api_client.maas_operator, True)
    confirmed_booking = baker.make(
        Booking,
        maas_operator=maas_api_client.maas_operator,
        ticketing_system=feed.ticketing_system,
        status=Booking.Status.CONFIRMED,
    )
    ticketing_system = feed.ticketing_system
    requests_mock.get(
        urljoin(ticketing_system.bookings_api_url, f"{confirmed_booking.source_id}/"),
        json=get_confirmations_data(confirmed_booking.source_id, include_qr=False),
        status_code=status.HTTP_200_OK,
    )

    response = maas_api_client.get(f"{ENDPOINT}{confirmed_booking.api_id}/")

    assert response.status_code == 200
    assert set(response.data.keys()) == {"id", "status", "tickets"}
    snapshot.assert_match(response.data["tickets"])
    assert Booking.objects.count() == 1


@pytest.mark.parametrize("endpoint", ("reservation", "confirmation", "retrieve"))
@pytest.mark.parametrize(
    "ticketing_api_response, ticketing_api_status_code",
    [
        (
            {
                "error": {
                    "code": "MAX_CAPACITY_EXCEEDED",
                }
            },
            422,
        ),
        (
            {
                "error": {
                    "code": "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED",
                    "message": "Maximum number of tickets requested exceeded.",
                }
            },
            400,
        ),
        (
            {
                "error": {
                    "code": "BOOKING_EXPIRED",
                    "message": "Booking expired.",
                    "details": "Your booking has been totally expired.",
                }
            },
            400,
        ),
        (
            {
                "error": {
                    "code": "BOOKING_ALREADY_CONFIRMED",
                }
            },
            422,
        ),
        (
            {
                "error": {
                    "code": "BOGUS_CODE",
                }
            },
            400,
        ),
        ({"error": {"no_code": "at_all"}}, 400),
        (
            {"error": {"code": "BOOKING_EXPIRED"}},
            500,
        ),
        (
            None,
            400,
        ),
        (
            None,
            200,
        ),
        (
            {},
            200,
        ),
        (
            {"id": "xyz"},
            201,
        ),
        (
            {"ID": "id_field_should_be_lowercase", "status": "RESERVED"},
            201,
        ),
        (
            {"id": "xyz", "status": "BOGUS_STATUS"},
            201,
        ),
        (
            {
                "error": {
                    "code": "MAX_CAPACITY_EXCEEDED",
                    "message": "",
                    "details": "",
                }
            },
            422,
        ),
        (
            {
                "error": {
                    "code": "BOOKING_ALREADY_CONFIRMED",
                    "message": "",
                    "details": "",
                }
            },
            422,
        ),
        (
            {
                "error": {
                    "code": "TICKET_SALES_ENDED",
                }
            },
            422,
        ),
        (
            {
                "error": {
                    "code": "BOOKING_NOT_CONFIRMED",
                    "message": "Booking is not confirmed. Confirm the booking to get it's details.",
                }
            },
            422,
        ),
    ],
)
@pytest.mark.django_db
def test_ticketing_system_errors(
    maas_operator,
    requests_mock,
    maas_api_client,
    booking_post_data,
    fare_test_data,
    endpoint,
    ticketing_api_response,
    ticketing_api_status_code,
    snapshot,
):
    ticketing_system = fare_test_data.feed.ticketing_system

    data_params = (
        {"json": ticketing_api_response}
        if ticketing_api_response is not None
        else {"text": "no json"}
    )

    if endpoint in ("reservation", "confirmation"):
        if endpoint == "reservation":
            mock_url = ticketing_system.bookings_api_url
            api_url = ENDPOINT
            post_data = booking_post_data
        else:
            reserved_booking = baker.make(
                Booking,
                maas_operator=maas_operator,
                source_id="test_confirmation_id",
                ticketing_system=ticketing_system,
            )
            mock_url = urljoin(
                ticketing_system.bookings_api_url,
                f"{reserved_booking.source_id}/confirm/",
            )
            api_url = f"{ENDPOINT}{reserved_booking.api_id}/confirm/"
            post_data = {}

        requests_mock.post(
            mock_url,
            status_code=ticketing_api_status_code,
            **data_params,
        )

        response = maas_api_client.post(api_url, post_data)
    else:
        confirmed_booking = baker.make(
            Booking,
            maas_operator=maas_operator,
            source_id="test_confirmation_id",
            ticketing_system=ticketing_system,
            status=Booking.Status.CONFIRMED,
        )
        mock_url = urljoin(
            ticketing_system.bookings_api_url, f"{confirmed_booking.source_id}/"
        )
        api_url = f"{ENDPOINT}{confirmed_booking.api_id}/"
        post_data = {}

        requests_mock.get(
            mock_url,
            status_code=ticketing_api_status_code,
            **data_params,
        )

        response = maas_api_client.get(api_url, post_data)

    assert requests_mock.call_count == 1
    assert response.status_code == 422

    snapshot.assert_match(response.json())


@pytest.mark.django_db
def test_fetch_availability(
    maas_api_client, maas_operator, requests_mock, api_id_generator, snapshot
):
    allowed_feed_1 = get_feed_for_maas_operator(maas_operator, True)
    allowed_feed_2 = get_feed_for_maas_operator(maas_operator, True)
    disallowed_feed = get_feed_for_maas_operator(maas_operator, False)

    allowed_ticketing_system_1 = allowed_feed_1.ticketing_system
    allowed_ticketing_system_2 = allowed_feed_2.ticketing_system
    disallowed_ticketing_system = disallowed_feed.ticketing_system

    allowed_ticketing_system_1.availability_api_url = "http://example.com/allowed1/"
    allowed_ticketing_system_1.save(update_fields=("availability_api_url",))

    allowed_ticketing_system_2.availability_api_url = "http://example.com/allowed2/"
    allowed_ticketing_system_2.save(update_fields=("availability_api_url",))

    disallowed_ticketing_system.availability_api_url = "http://example.com/disallowed/"
    disallowed_ticketing_system.save(update_fields=("availability_api_url",))

    # both of these should be returned by the first ticketing system
    allowed_departures_1 = baker.make(
        Departure,
        trip__feed=allowed_feed_1,
        trip__source_id=seq("source_id of trip "),
        api_id=api_id_generator,
        date=datetime.date(2021, 4, 28),
        _quantity=2,
    )

    # the second ticketing system returns only the second one of these
    allowed_departures_2 = baker.make(
        Departure,
        trip__feed=allowed_feed_2,
        trip__source_id=seq("source_id of trip ", start=3),
        api_id=api_id_generator,
        date=datetime.date(2021, 4, 29),
        _quantity=2,
    )

    # this will not be in the returned results because it is from a ticketing system we
    # don't have a permission for
    disallowed_departure = baker.make(
        Departure,
        trip__feed=disallowed_feed,
        trip__source_id=seq("source_id of trip ", start=5),
        api_id=api_id_generator,
        date=datetime.date(2021, 4, 30),
    )

    requests_mock.post(
        allowed_ticketing_system_1.availability_api_url,
        json=[
            {
                "trip_id": allowed_departures_1[0].trip.source_id,
                "date": str(allowed_departures_1[0].date),
                "available": 1,
                "total": 10,
            },
            {
                "trip_id": allowed_departures_1[1].trip.source_id,
                "date": str(allowed_departures_1[1].date),
                "available": 5,
            },
        ],
        status_code=status.HTTP_200_OK,
    )

    requests_mock.post(
        allowed_ticketing_system_2.availability_api_url,
        json=[
            {
                "trip_id": allowed_departures_2[1].trip.source_id,
                "date": str(allowed_departures_2[1].date),
                "available": 0,
                "total": 100,
            },
        ],
        status_code=status.HTTP_200_OK,
    )

    departures_to_fetch = (
        allowed_departures_1 + allowed_departures_2 + [disallowed_departure]
    )

    response = maas_api_client.post(
        f"{ENDPOINT}availability/",
        {"departure_ids": [d.api_id for d in departures_to_fetch]},
    )

    for i, request in enumerate(requests_mock.request_history, 1):
        snapshot.assert_match(request.url, name=f"request {i} url")
        snapshot.assert_match(request.json(), name=f"request {i} body")

    snapshot.assert_match(json.loads(response.content), name="response")
