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
