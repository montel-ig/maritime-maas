import pytest
from model_bakery import baker

from gtfs.models import Feed, Route, Stop
from gtfs.tests.utils import get_feed_for_maas_operator
from maas.models import MaasOperator


def get_unrelated_feeds():
    """Get a feed without maas operator and with a different maas operator."""
    unattached_feed = get_feed_for_maas_operator(None, False)
    another_maas_operator = baker.make(MaasOperator)
    different_maas_operator_feed = get_feed_for_maas_operator(
        another_maas_operator, True
    )
    return unattached_feed, different_maas_operator_feed


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_filtering_feeds_for_maas_operators(maas_operator, has_permission):
    unattached_feed, different_maas_operator_feed = get_unrelated_feeds()
    feed = get_feed_for_maas_operator(maas_operator, has_permission)

    feeds = Feed.objects.for_maas_operator(maas_operator)

    if has_permission:
        assert feed in feeds
    else:
        assert feed not in feeds
    assert unattached_feed not in feeds
    assert different_maas_operator_feed not in feeds


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_filtering_routes_for_maas_operator(maas_operator, has_permission):
    unattached_feed, different_maas_operator_feed = get_unrelated_feeds()
    unexpected_route_1 = baker.make(Route, feed=unattached_feed)
    unexpected_route_2 = baker.make(Route, feed=different_maas_operator_feed)
    feed = get_feed_for_maas_operator(maas_operator, has_permission)
    route = baker.make(Route, feed=feed)

    routes = Route.objects.for_maas_operator(maas_operator)

    if has_permission:
        assert route in routes
    else:
        assert route not in routes
    assert unexpected_route_1 not in routes
    assert unexpected_route_2 not in routes


@pytest.mark.django_db
@pytest.mark.parametrize("has_permission", [True, False])
def test_filtering_stops_for_maas_operator(maas_operator, has_permission):
    unattached_feed, different_maas_operator_feed = get_unrelated_feeds()
    unexpected_stop_1 = baker.make(Stop, feed=unattached_feed)
    unexpected_stop_2 = baker.make(Stop, feed=different_maas_operator_feed)
    feed = get_feed_for_maas_operator(maas_operator, has_permission)
    stop = baker.make(Stop, feed=feed)

    stops = Stop.objects.for_maas_operator(maas_operator)

    if has_permission:
        assert stop in stops
    else:
        assert stop not in stops
    assert unexpected_stop_1 not in stops
    assert unexpected_stop_2 not in stops
