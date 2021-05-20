from urllib.parse import quote, urljoin

import pytest
from model_bakery import baker
from rest_framework import status

from bookings.models import Booking
from bookings.ticketing_system import TicketingSystemAPI
from gtfs.tests.utils import get_feed_for_maas_operator
from mock_ticket_api.utils import get_confirmations_data, get_reservation_data


@pytest.mark.django_db
def test_api_call_for_reservation(
    maas_operator, fare_test_data, requests_mock, snapshot
):
    ticketing_system = fare_test_data.feed.ticketing_system
    requests_mock.post(
        ticketing_system.api_url,
        json=get_reservation_data(),
        status_code=status.HTTP_201_CREATED,
    )
    ticket_data = {
        "route": fare_test_data.routes[0],
        "departures": [fare_test_data.departures[0]],
        "tickets": [
            {
                "fare": fare_test_data.fares[0],
                "fare_rider_category": fare_test_data.rider_categories[0],
            }
        ],
        "locale": "fi",
        "request_id": "requestID",
        "transaction_id": "transactionID",
    }

    Booking.objects.create_reservation(maas_operator, ticketing_system, ticket_data)

    assert requests_mock.call_count == 1
    snapshot.assert_match(requests_mock.request_history[0].json())
    assert requests_mock.request_history[0].headers["Authorization"] == "Bearer APIKEY"


@pytest.mark.django_db
def test_api_call_for_confirmation(maas_operator, requests_mock, snapshot):
    feed = get_feed_for_maas_operator(maas_operator, True)
    extra_params = {
        "locale": "fi",
        "request_id": "requestID",
        "transaction_id": "transactionID",
    }
    reserved_booking = baker.make(
        Booking,
        maas_operator=maas_operator,
        source_id="test_confirmation_id",
        ticketing_system=feed.ticketing_system,
    )
    ticketing_system = feed.ticketing_system
    requests_mock.post(
        urljoin(ticketing_system.api_url, f"{reserved_booking.source_id}/confirm/"),
        json=get_confirmations_data(reserved_booking.source_id, include_qr=False),
        status_code=status.HTTP_200_OK,
    )

    reserved_booking.confirm(passed_parameters=extra_params)

    assert requests_mock.call_count == 1
    snapshot.assert_match(requests_mock.request_history[0].json())
    assert requests_mock.request_history[0].headers["Authorization"] == "Bearer APIKEY"


@pytest.mark.django_db
def test_ticket_system_call_use_quoted_identifiers(maas_operator, requests_mock):
    identifier = "MAAS:5154.1621500322898.jxgTgw,11E8"
    feed = get_feed_for_maas_operator(maas_operator, True)
    ticketing_system = feed.ticketing_system
    requests_mock.post(
        urljoin(ticketing_system.api_url, f"{quote(identifier)}/confirm/"),
        json=get_confirmations_data(identifier, include_qr=False),
        status_code=status.HTTP_200_OK,
    )

    api = TicketingSystemAPI(
        ticketing_system=ticketing_system, maas_operator=maas_operator
    )

    data = api.confirm(identifier)
    assert data["status"] == "CONFIRMED"
