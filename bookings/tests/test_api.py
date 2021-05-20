import json
import uuid
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status

from bookings.models import Booking
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
        ticketing_system.api_url,
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
        ticketing_system.api_url,
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
        urljoin(ticketing_system.api_url, f"{reserved_booking.source_id}/confirm/"),
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
        urljoin(ticketing_system.api_url, f"{reserved_booking.source_id}/confirm/"),
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


@pytest.mark.parametrize("endpoint", ("reservation", "confirmation"))
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

    if endpoint == "reservation":
        mock_url = ticketing_system.api_url
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
            ticketing_system.api_url, f"{reserved_booking.source_id}/confirm/"
        )
        api_url = f"{ENDPOINT}{reserved_booking.api_id}/confirm/"
        post_data = {}

    requests_mock.post(
        mock_url,
        status_code=ticketing_api_status_code,
        **data_params,
    )

    response = maas_api_client.post(api_url, post_data)

    assert requests_mock.call_count == 1
    assert response.status_code == 422

    snapshot.assert_match(response.json())
