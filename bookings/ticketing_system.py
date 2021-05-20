from json import JSONDecodeError
from typing import Optional
from urllib.parse import quote, urljoin

import requests
from requests import RequestException
from rest_framework import serializers

from maas.models import MaasOperator, TicketingSystem

from .choices import BookingStatus
from .utils import TokenAuth

reservation_error_codes = (
    "MAX_CAPACITY_EXCEEDED",
    "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED",
)

confirmation_error_codes = (
    "BOOKING_EXPIRED",
    "BOOKING_ALREADY_CONFIRMED",
)


class TicketingSystemRequestError(Exception):
    def __init__(self, code, message=None, details=None):
        self.code = code
        self.message = message or ""
        self.details = details or ""


class TicketingSystemNotBehavingError(Exception):
    code = "TICKET_SYSTEM_ERROR"
    message = ""
    details = ""

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return (
            f"Ticketing system error: {self.__cause__} "
            f"response: ({self.response.status_code}) {self.response.content}"
        )


class ReservationSuccessSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=[BookingStatus.RESERVED])


class ConfirmationSuccessSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=[BookingStatus.CONFIRMED])
    tickets = serializers.ListField(allow_empty=False)


class InnerReservationErrorSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=reservation_error_codes)
    message = serializers.CharField(required=False, allow_blank=True)
    details = serializers.CharField(required=False, allow_blank=True)


class InnerConfirmationErrorSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=confirmation_error_codes)
    message = serializers.CharField(required=False, allow_blank=True)
    details = serializers.CharField(required=False, allow_blank=True)


class ReservationErrorSerializer(serializers.Serializer):
    error = InnerReservationErrorSerializer()


class ConfirmationErrorSerializer(serializers.Serializer):
    error = InnerConfirmationErrorSerializer()


class TicketingSystemAPI:
    TIMEOUT = 10

    def __init__(self, ticketing_system: TicketingSystem, maas_operator: MaasOperator):
        self.ticketing_system = ticketing_system
        self.maas_operator = maas_operator

    def reserve(self, ticket_data: dict):
        url = self.ticketing_system.api_url
        return self._post(
            url, ticket_data, ReservationSuccessSerializer, ReservationErrorSerializer
        )

    def confirm(self, identifier: str, passed_parameters: Optional[dict] = None):
        url = urljoin(self.ticketing_system.api_url, f"{quote(identifier)}/confirm/")
        return self._post(
            url,
            passed_parameters or {},
            ConfirmationSuccessSerializer,
            ConfirmationErrorSerializer,
        )

    def _post(self, url: str, data, success_serializer, error_serializer):
        from bookings.serializers import ApiBookingSerializer

        payload = ApiBookingSerializer(
            {**data, "maas_operator": self.maas_operator}
        ).data

        if not self.ticketing_system.api_key:
            raise Exception("Ticketing system doesn't define an API key.")

        response = requests.post(
            url,
            json=payload,
            timeout=self.TIMEOUT,
            auth=TokenAuth(self.ticketing_system.api_key),
        )

        try:
            data = response.json()
            if 400 <= response.status_code <= 499:
                serializer = error_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                raise TicketingSystemRequestError(**serializer.data["error"])
            response.raise_for_status()

            serializer = success_serializer(data=data)
            serializer.is_valid(raise_exception=True)

        except (JSONDecodeError, serializers.ValidationError, RequestException) as e:
            raise TicketingSystemNotBehavingError(response=response) from e

        return serializer.validated_data
