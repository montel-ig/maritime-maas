from copy import deepcopy

from model_bakery import baker

from gtfs.models import Feed
from maas.models import TicketingSystem, TransportServiceProvider


def get_feed_for_maas_operator(maas_operator, has_permission):
    ticketing_system = baker.make(TicketingSystem, api_key="APIKEY")
    feed = baker.make(Feed, ticketing_system=ticketing_system)
    transport_service_provider = baker.make(
        TransportServiceProvider, ticketing_system=ticketing_system
    )
    if has_permission:
        maas_operator.transport_service_providers.add(transport_service_provider)

    return feed


def clean_stop_for_snapshot(stop):
    assert set(stop["coordinates"]) == {"latitude", "longitude"}
    # we don't want no floats in our snapshots
    return {k: v for k, v in stop.items() if k != "coordinates"}


def clean_stops_for_snapshot(stops):
    return [clean_stop_for_snapshot(s) for s in stops]


def clean_shape_for_snapshot(shape):
    if not shape:
        return shape
    shape = deepcopy(shape)
    # we don't want no floats in our snapshots
    shape["geometry"].pop("coordinates")
    return shape


def clean_shapes_for_snapshot(shapes):
    return [clean_shape_for_snapshot(s) for s in shapes]
