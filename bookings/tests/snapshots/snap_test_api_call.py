# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_api_call_for_confirmation 1"] = {
    "maas_operator_id": "name of maas operator 1"
}

snapshots["test_api_call_for_reservation 1"] = {
    "departures": [{"date": "2021-04-28", "trip_id": "source_id of trip 1"}],
    "locale": "fi",
    "maas_operator_id": "name of maas operator 1",
    "route_id": "source_id of route 1",
    "tickets": [
        {
            "customer_type_id": "source_id of test rider category 1",
            "ticket_type_id": "source_id of test fare 1",
        }
    ],
}
