import pytest
import json
from model_bakery import baker
from gtfs.models import Route, Stop, Feed


@pytest.mark.django_db
def test_routes(api_client):

    endpoint = "/v1/routes/"

    feed = baker.make(Feed)
    baker.make(Route, feed=feed)
    baker.make(Stop, feed=feed)

    response = api_client().get(endpoint)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 1


@pytest.mark.django_db
def test_routes_with_stop_id(api_client):

    routes = baker.make(Route, _quantity=3)
    stop = baker.make(Stop, feed=routes[0].feed)

    endpoint = "/v1/routes/"
    url = f"{endpoint}?stopId={stop.id}"

    response = api_client().get(url)

    assert response.status_code == 200
    assert len(json.loads(response.content)) == 1
