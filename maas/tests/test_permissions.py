import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

from maas.models import MaasOperator
from maas.permissions import IsMaasOperator

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize("is_maas_operator", [True, False])
def test_test_maas_operator_permission(rf, is_maas_operator):
    permission_check = IsMaasOperator()
    if is_maas_operator:
        user = baker.make(MaasOperator).user
    else:
        user = baker.make(User)

    requests = [
        rf.get("/"),
        rf.post("/"),
        rf.delete("/"),
        rf.put("/"),
        rf.patch("/"),
    ]

    for r in requests:
        r.user = user

        permission = permission_check.has_permission(r, None)
        assert permission if is_maas_operator else not permission
