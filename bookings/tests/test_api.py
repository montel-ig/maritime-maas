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


@pytest.mark.django_db
@pytest.mark.parametrize("has_route", [True, False])
def test_create_booking(maas_api_client, has_route, fare_test_data, requests_mock):
    ticketing_system = fare_test_data.feed.ticketing_system
    requests_mock.post(
        ticketing_system.api_url,
        json=get_reservation_data(),
        status_code=status.HTTP_201_CREATED,
    )
    post_data = {
        "departure_ids": [fare_test_data.departures[0].api_id],
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

    assert response.status_code == 201
    assert {"id", "status"} == set(response.data.keys())
    assert Booking.objects.count() == 1
    assert Booking.objects.first().status == Booking.Status.RESERVED


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

    response = maas_api_client.post(f"{ENDPOINT}{reserved_booking.api_id}/confirm/")

    assert response.status_code == 200
    assert {"id", "status", "tickets"} == set(response.data.keys())
    snapshot.assert_match(response.data["tickets"])
    assert Booking.objects.count() == 1
    booking = Booking.objects.get(pk=reserved_booking.pk)
    assert booking.status == Booking.Status.CONFIRMED
    assert booking.source_id == expected_source_id


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
