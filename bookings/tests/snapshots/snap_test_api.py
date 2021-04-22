# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_create_booking_illegal_departures[False-departure_indices2] 1"] = {
    "departure_ids": ["All departures must belong to the same route."]
}

snapshots["test_create_booking_illegal_departures[True-departure_indices0] 1"] = {
    "departure_ids": ["All departures must belong to the same route."]
}

snapshots["test_create_booking_illegal_departures[True-departure_indices1] 1"] = {
    "departure_ids": ["All departures must belong to the same route."]
}

snapshots["test_create_booking_illegal_rider_category_or_fare[0-1] 1"] = {
    "tickets": [
        {
            "ticket_type_id": [
                'Invalid ID "00000000-0000-0000-0000-000000000001" - object does not exist.'
            ]
        }
    ]
}

snapshots["test_create_booking_illegal_rider_category_or_fare[1-0] 1"] = {
    "tickets": [
        {
            "customer_type_id": [
                'Invalid ID "00000000-0000-0000-0000-000000000003" - object does not exist.'
            ]
        }
    ]
}

snapshots["test_create_booking_illegal_rider_category_or_fare[1-1] 1"] = {
    "tickets": [
        {
            "ticket_type_id": [
                'Invalid ID "00000000-0000-0000-0000-000000000001" - object does not exist.'
            ]
        }
    ]
}

snapshots["test_create_booking_no_permission 1"] = {
    "departure_ids": [
        'Invalid ID "00000000-0000-0000-0000-000000000004" - object does not exist.'
    ]
}
