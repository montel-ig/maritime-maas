import json
from unittest.mock import patch
from uuid import UUID

import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.test import APIClient


@pytest.fixture
def ticket_api_client():
    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION="Bearer 70k3n")
    return api_client


params = {"maas_operator_id": "00000000-0000-0000-0000-000000000001", "locale": "fi"}


@patch("uuid.uuid4", lambda: UUID(int=1))
def test_ticket_reservation(ticket_api_client, snapshot):
    response = ticket_api_client.post(
        reverse("mockapi-list"), {"ticket": "please", **params}
    )

    snapshot.assert_match(json.loads(response.content))


@freeze_time("2021-04-20")
def test_ticket_confirmation(ticket_api_client, snapshot):
    response = ticket_api_client.post(
        reverse("mockapi-confirm", kwargs={"pk": "71ck37_1d"}), params
    )

    snapshot.assert_match(json.loads(response.content))


@freeze_time("2021-04-20")
def test_ticket_details(ticket_api_client, snapshot):
    response = ticket_api_client.get(
        reverse("mockapi-detail", kwargs={"pk": "71ck37_1d"}),
        HTTP_ACCEPT_LANGUAGE="sv",
    )

    snapshot.assert_match(json.loads(response.content))
    assert response.headers["Content-Language"] == "sv"


@pytest.mark.parametrize(
    "error",
    [
        "MAX_CAPACITY_EXCEEDED",
        "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED",
        "BOOKING_EXPIRED",
        "BOOKING_ALREADY_CONFIRMED",
        "TICKET_SYSTEM_ERROR",
        "BOOKING_NOT_CONFIRMED",
    ],
)
@pytest.mark.parametrize("method", ["reserve", "confirm", "retrieve"])
def test_mock_api_errors(ticket_api_client, error, method):
    response = None
    if method == "reserve":
        response = ticket_api_client.post(
            reverse("mockapi-list"),
            {"ticket": "please", "request_id": error, **params},
        )
    elif method == "confirm":
        response = ticket_api_client.post(
            reverse("mockapi-confirm", kwargs={"pk": "71ck37_1d"}),
            {"request_id": error, **params},
        )
    elif method == "retrieve":
        response = ticket_api_client.get(
            reverse("mockapi-detail", kwargs={"pk": "71ck37_1d"}), {"request_id": error}
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == error
