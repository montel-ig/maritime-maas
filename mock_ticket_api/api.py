from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mock_ticket_api.utils import (
    get_confirmations_data,
    get_error_data,
    get_reservation_data,
)


class MockTicketParamsSerializer(serializers.Serializer):
    maas_operator_id = serializers.CharField()
    locale = serializers.ChoiceField(choices=settings.TICKET_LANGUAGES, required=False)
    request_id = serializers.CharField(required=False, allow_blank=True)


@extend_schema_view(
    create=extend_schema(exclude=True), confirm=extend_schema(exclude=True)
)
class MockTicketViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = MockTicketParamsSerializer

    def create(self, request):
        params = self.serializer_class(data=request.data)
        if not params.is_valid():
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

        if error_data := get_error_data(params.data.get("request_id")):
            return Response(
                error_data,
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(get_reservation_data(), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        params = self.serializer_class(data=request.data)
        if not params.is_valid():
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

        if error_data := get_error_data(params.data.get("request_id")):
            return Response(
                error_data,
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(get_confirmations_data(pk), status=status.HTTP_200_OK)
