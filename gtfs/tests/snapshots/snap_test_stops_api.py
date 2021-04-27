# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_stops 1"] = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "stop 1",
        "tts_name": "tts_name of stop 1",
        "wheelchair_boarding": 0,
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "stop 2",
        "tts_name": "tts_name of stop 2",
        "wheelchair_boarding": 0,
    },
]

snapshots["test_stops_departures[filters2] 1"] = [
    {
        "arrival_time": "2021-02-18T13:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip 1",
        "departure_time": "2021-02-18T13:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000003",
        "route_id": "00000000-0000-0000-0000-000000000000",
        "short_name": "short_name of test trip 1",
        "stop_headsign": "stop_headsign of test stop time 1",
        "stop_sequence": 1,
        "stop_timepoint": 1,
        "wheelchair_accessible": 0,
    },
    {
        "arrival_time": "2021-02-18T13:15:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 2",
        "departure_headsign": "headsign of test trip 2",
        "departure_time": "2021-02-18T13:15:00Z",
        "direction_id": 1,
        "id": "00000000-0000-0000-0000-000000000004",
        "route_id": "00000000-0000-0000-0000-000000000000",
        "short_name": "short_name of test trip 2",
        "stop_headsign": "stop_headsign of test stop time 2",
        "stop_sequence": 1,
        "stop_timepoint": 1,
        "wheelchair_accessible": 0,
    },
]

snapshots["test_stops_departures[filters3] 1"] = [
    {
        "arrival_time": "2021-02-19T13:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip 1",
        "departure_time": "2021-02-19T13:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000005",
        "route_id": "00000000-0000-0000-0000-000000000000",
        "short_name": "short_name of test trip 1",
        "stop_headsign": "stop_headsign of test stop time 1",
        "stop_sequence": 1,
        "stop_timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_stops_departures[filters4] 1"] = [
    {
        "arrival_time": "2021-02-18T13:00:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 1",
        "departure_headsign": "headsign of test trip 1",
        "departure_time": "2021-02-18T13:00:00Z",
        "direction_id": 0,
        "id": "00000000-0000-0000-0000-000000000003",
        "route_id": "00000000-0000-0000-0000-000000000000",
        "short_name": "short_name of test trip 1",
        "stop_headsign": "stop_headsign of test stop time 1",
        "stop_sequence": 1,
        "stop_timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_stops_departures[filters5] 1"] = [
    {
        "arrival_time": "2021-02-18T13:15:00Z",
        "bikes_allowed": 0,
        "block_id": "block_id of test trip 2",
        "departure_headsign": "headsign of test trip 2",
        "departure_time": "2021-02-18T13:15:00Z",
        "direction_id": 1,
        "id": "00000000-0000-0000-0000-000000000004",
        "route_id": "00000000-0000-0000-0000-000000000000",
        "short_name": "short_name of test trip 2",
        "stop_headsign": "stop_headsign of test stop time 2",
        "stop_sequence": 1,
        "stop_timepoint": 1,
        "wheelchair_accessible": 0,
    }
]

snapshots["test_stops_departures[filters6] 1"] = []
