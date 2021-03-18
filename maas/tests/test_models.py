import pytest

from ..models import MaasOperator


@pytest.mark.django_db
def test_maas_operator_api_token_generation():
    operator = MaasOperator.objects.create(name="MaaS")
    assert len(operator.api_token)
