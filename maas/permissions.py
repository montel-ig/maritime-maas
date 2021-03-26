from rest_framework import permissions

from .models import MaasOperator


class IsMaasOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow only MaaS operators to proceed further.
        """
        user = request.user

        if not user.is_authenticated:
            return False

        try:
            user.maas_operator
            return True
        except MaasOperator.DoesNotExist:
            pass

        return False
