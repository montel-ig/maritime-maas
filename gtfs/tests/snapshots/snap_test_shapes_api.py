# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_shapes[filtering0] 1"] = {
    "__all__": ['Either "route_id" or "departure_id" is required.']
}

snapshots["test_shapes[filtering1] 1"] = [
    {"geometry": {"type": "LineString"}, "id": "deadbeef-0000-0000-0000-000000000000"},
    {"geometry": {"type": "LineString"}, "id": "babeface-0000-0000-0000-000000000000"},
]

snapshots["test_shapes[filtering2] 1"] = [
    {"geometry": {"type": "LineString"}, "id": "c0ffee00-0000-0000-0000-000000000000"}
]

snapshots["test_shapes[filtering3] 1"] = [
    {"geometry": {"type": "LineString"}, "id": "deadbeef-0000-0000-0000-000000000000"}
]

snapshots["test_shapes[filtering4] 1"] = [
    {"geometry": {"type": "LineString"}, "id": "c0ffee00-0000-0000-0000-000000000000"}
]
