import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from maas.models import MaasOperator
from maas.tests.utils import token_authenticate


@pytest.fixture
def maas_operator():
    return baker.make(MaasOperator)


@pytest.fixture
def maas_api_client(maas_operator):
    api_client = APIClient()
    token_authenticate(api_client, maas_operator.user)
    api_client.maas_operator = maas_operator
    return api_client
