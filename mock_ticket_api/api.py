import base64
import datetime
import uuid
from pathlib import PurePath

from django.utils import timezone
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


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

        return Response(
            {"id": str(uuid.uuid4()), "status": "RESERVED"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        params = self.serializer_class(data=request.data)
        if not params.is_valid():
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

        path = PurePath(__file__).parent.joinpath("data", "ticket_qr.png")
        with open(path.as_posix(), "rb") as f:
            ticket = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        valid_from = timezone.now()
        departed_at = valid_from + datetime.timedelta(hours=1)
        valid_to = valid_from + datetime.timedelta(days=1)

        return Response(
            {
                "id": pk,
                "status": "CONFIRMED",
                "tickets": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "qr_code": ticket,
                        "departures": [
                            {
                                "from": "Kauppatori",
                                "to": "Vallisaari",
                                "depart_at": self.format_timestamp(departed_at),
                            }
                        ],
                        "name": "Day in Vallisaari",
                        "description": "This is the description of the ticket",
                        "instructions": "These are the instructions of the ticket",
                        "agency": {
                            "name": "MaaS Line",
                            "logo_url": "http://www.agency.com/logo.png",
                        },
                        "ticket_html": "<div>...</div>",
                        "ticket_type": "Päivälippu",
                        "customer_type": "Aikuinen",
                        "amount": 12,
                        "currency": "EUR",
                        "terms_of_use": "http://www.terms.and.conditions.fi",
                        "locale": "fi",
                        "valid_from": self.format_timestamp(valid_from),
                        "valid_to": self.format_timestamp(valid_to),
                        "refresh_at": self.format_timestamp(valid_to),
                    }
                ],
            },
            status=status.HTTP_200_OK,
        )

    def format_timestamp(self, d: datetime.datetime):
        return f"{d.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"
