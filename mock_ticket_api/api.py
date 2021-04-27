from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mock_ticket_api.utils import get_confirmations_data, get_reservation_data


class MockTicketParamsSerializer(serializers.Serializer):
    maas_operator_id = serializers.UUIDField()
    locale = serializers.ChoiceField(choices=("fi", "sv", "en"), required=False)


class MockTicketViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]
    serializer_class = MockTicketParamsSerializer

    def create(self, request):
        params = self.serializer_class(data=request.data)
        if not params.is_valid():
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(get_reservation_data(), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        params = self.serializer_class(data=request.data)
        if not params.is_valid():
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(get_confirmations_data(pk), status=status.HTTP_200_OK)
