# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_rider_categories_with_prices 1"] = [
    {
        "customer_types": [
            {
                "currency_type": "EUR",
                "description": "description of test rider category 1",
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "name of test rider category 1",
                "price": "1.00",
            },
            {
                "currency_type": "EUR",
                "description": "description of test rider category 2",
                "id": "00000000-0000-0000-0000-000000000002",
                "name": "name of test rider category 2",
                "price": "2.00",
            },
            {
                "currency_type": "EUR",
                "description": "description of test rider category 3",
                "id": "00000000-0000-0000-0000-000000000003",
                "name": "name of test rider category 3",
                "price": "3.00",
            },
        ],
        "description": "Description",
        "id": "00000000-0000-0000-0000-000000000000",
        "instructions": "Instructions",
        "name": "Name",
    }
]

snapshots["test_routes 1"] = [
    {
        "agency": {
            "email": "test-agency@example.com",
            "logo_url": "www.testagency.com/logo",
            "name": "test agency",
            "phone": "777777",
            "url": "www.testagency.com",
        },
        "capacity_sales": 0,
        "description": "desc of test route ",
        "id": "00000000-0000-0000-0000-000000000000",
        "name": "",
        "stops": [
            {
                "description": "desc of test stop ",
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "stop ",
                "tts_name": "tts_name of stop ",
                "wheelchair_boarding": 0,
            },
            {
                "description": "desc of test stop ",
                "id": "00000000-0000-0000-0000-000000000002",
                "name": "stop ",
                "tts_name": "tts_name of stop ",
                "wheelchair_boarding": 0,
            },
        ],
        "ticket_types": [],
        "url": "url of test route ",
    }
]

snapshots["test_routes_departures[filters2] 1"] = [
    {
        "arrival_time": "2021-02-18T13:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-18T13:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000003",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 1,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    },
    {
        "arrival_time": "2021-02-18T13:15:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 2",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-18T13:15:00Z",
        "direction_id": 1,
        "id": "00000000-0000-0000-0000-000000000004",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 1,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    },
]

snapshots["test_routes_departures[filters2] 2"] = [
    {
        "arrival_time": "2021-02-19T00:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-19T01:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000003",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 2,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    },
    {
        "arrival_time": "2021-02-19T00:15:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 2",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-19T01:15:00Z",
        "direction_id": 1,
        "id": "00000000-0000-0000-0000-000000000004",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 2,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    },
]

snapshots["test_routes_departures[filters3] 1"] = [
    {
        "arrival_time": "2021-02-19T13:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-19T13:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000005",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 1,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_routes_departures[filters3] 2"] = [
    {
        "arrival_time": "2021-02-20T00:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-20T01:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000005",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 2,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_routes_departures[filters4] 1"] = [
    {
        "arrival_time": "2021-02-18T13:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-18T13:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000003",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 1,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_routes_departures[filters4] 2"] = [
    {
        "arrival_time": "2021-02-19T00:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-19T01:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000003",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 2,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_routes_departures[filters5] 1"] = [
    {
        "arrival_time": "2021-02-18T13:15:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 2",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-18T13:15:00Z",
        "direction_id": 1,
        "id": "00000000-0000-0000-0000-000000000004",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 1,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_routes_departures[filters5] 2"] = [
    {
        "arrival_time": "2021-02-19T00:15:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 2",
        "departure_headsign": "headsign of test trip ",
        "departure_time": "2021-02-19T01:15:00Z",
        "direction_id": 1,
        "id": "00000000-0000-0000-0000-000000000004",
        "short_name": "short_name of test trip ",
        "stop_headsign": "stop_headsign of test stop time ",
        "stop_sequence": 2,
        "timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_routes_departures[filters6] 1"] = []

snapshots["test_routes_departures[filters6] 2"] = []
