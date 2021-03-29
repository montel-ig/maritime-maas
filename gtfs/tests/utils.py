from model_bakery import baker

from gtfs.models import Feed
from maas.models import TicketingSystem, TransportServiceProvider


def get_feed_for_maas_operator(maas_operator, has_permission):
    ticketing_system = baker.make(TicketingSystem)
    feed = baker.make(Feed, ticketing_system=ticketing_system)
    transport_service_provider = baker.make(
        TransportServiceProvider, ticketing_system=ticketing_system
    )
    if has_permission:
        maas_operator.transport_service_providers.add(transport_service_provider)

    return feed
