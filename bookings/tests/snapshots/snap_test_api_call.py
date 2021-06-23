# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_api_call_for_confirmation 1"] = {
    "locale": "fi",
    "maas_operator_id": "identifier of maas operator 1",
    "request_id": "requestID",
    "transaction_id": "transactionID",
}

snapshots[
    "test_api_call_for_confirmation 2"
] = 'Ticketing system API call - URL: https://api.example.com/test_confirmation_id/confirm/ data: {"request_id": "requestID", "transaction_id": "transactionID", "locale": "fi", "maas_operator_id": "identifier of maas operator 1"}'  # noqa: E501

snapshots["test_api_call_for_reservation 1"] = {
    "departures": [{"date": "2021-04-28", "trip_id": "source_id of trip 1"}],
    "locale": "fi",
    "maas_operator_id": "identifier of maas operator 1",
    "request_id": "requestID",
    "route_id": "source_id of route 1",
    "tickets": [
        {
            "customer_type_id": "source_id of test rider category 1",
            "ticket_type_id": "source_id of test fare 1",
        }
    ],
    "transaction_id": "transactionID",
}

snapshots[
    "test_api_call_for_reservation 2"
] = 'Ticketing system API call - URL: https://api.example.com data: {"request_id": "requestID", "transaction_id": "transactionID", "locale": "fi", "maas_operator_id": "identifier of maas operator 1", "route_id": "source_id of route 1", "departures": [{"trip_id": "source_id of trip 1", "date": "2021-04-28"}], "tickets": [{"ticket_type_id": "source_id of test fare 1", "customer_type_id": "source_id of test rider category 1"}]}'  # noqa: E501
