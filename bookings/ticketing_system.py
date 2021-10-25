import json
import logging
from json import JSONDecodeError
from typing import Optional, Tuple, Type
from urllib.parse import quote, urljoin

import requests
from requests import RequestException
from rest_framework import serializers

from maas.models import MaasOperator, TicketingSystem

from .choices import BookingStatus
from .utils import TokenAuth

logger = logging.getLogger(__name__)

ErrorCodes = Optional[Tuple[str, ...]]

reservation_error_codes = (
    "MAX_CAPACITY_EXCEEDED",
    "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED",
    "TICKET_SALES_ENDED",
)

confirmation_error_codes = (
    "BOOKING_EXPIRED",
    "BOOKING_ALREADY_CONFIRMED",
    "TICKET_SALES_ENDED",
)

retrieve_error_codes = ("BOOKING_NOT_CONFIRMED",)


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


class AvailabilitySuccessSerializer(serializers.Serializer):
    # stupid hax to get this serializer initialized with many=True in
    # _process_response()
    _many = True

    trip_id = serializers.CharField()
    date = serializers.DateField()
    available = serializers.IntegerField(min_value=0)
    total = serializers.IntegerField(min_value=0, required=False)


def _build_error_serializer(
    error_codes: ErrorCodes = None,
) -> Type[serializers.Serializer]:
    class InnerErrorSerializer(serializers.Serializer):
        code = serializers.ChoiceField(choices=error_codes or ())
        message = serializers.CharField(required=False, allow_blank=True)
        details = serializers.CharField(required=False, allow_blank=True)

    class ErrorSerializer(serializers.Serializer):
        error = InnerErrorSerializer()

    return ErrorSerializer


class TicketingSystemAPI:
    TIMEOUT = 10

    def __init__(self, ticketing_system: TicketingSystem, maas_operator: MaasOperator):
        self.ticketing_system = ticketing_system
        self.maas_operator = maas_operator

    def reserve(self, ticket_data: dict):
        from bookings.serializers import ApiBookingSerializer

        url = self.ticketing_system.bookings_api_url
        payload = ApiBookingSerializer(
            {**ticket_data, "maas_operator": self.maas_operator}
        ).data

        return self._post(
            url, payload, ReservationSuccessSerializer, reservation_error_codes
        )

    def confirm(self, identifier: str, passed_parameters: Optional[dict] = None):
        from bookings.serializers import ApiBookingSerializer

        url = urljoin(
            self.ticketing_system.bookings_api_url, f"{quote(identifier)}/confirm/"
        )
        payload = ApiBookingSerializer(
            {**(passed_parameters or {}), "maas_operator": self.maas_operator}
        ).data

        return self._post(
            url,
            payload,
            ConfirmationSuccessSerializer,
            confirmation_error_codes,
        )

    def retrieve(self, identifier: str, passed_parameters: Optional[dict] = None):
        url = urljoin(self.ticketing_system.bookings_api_url, f"{quote(identifier)}/")

        return self._get(
            url,
            passed_parameters or {},
            ConfirmationSuccessSerializer,
            retrieve_error_codes,
        )

    def availability(self, departures):
        if not (url := self.ticketing_system.availability_api_url):
            return []

        from .serializers import ApiAvailabilitySerializer

        departures_data = ApiAvailabilitySerializer(departures, many=True).data

        return self._post(
            url,
            {"departures": departures_data},
            AvailabilitySuccessSerializer,
        )

    def _get(
        self,
        url: str,
        passed_parameters,
        success_serializer: Type[serializers.Serializer],
        error_codes: ErrorCodes = None,
    ):
        if not self.ticketing_system.api_key:
            raise Exception("Ticketing system doesn't define an API key.")

        logger.info(f"Ticketing system API call - GET {url}")

        response = requests.get(
            url,
            params=passed_parameters,
            timeout=self.TIMEOUT,
            auth=TokenAuth(self.ticketing_system.api_key),
        )

        return self._process_response(response, success_serializer, error_codes)

    def _post(
        self,
        url: str,
        payload,
        success_serializer: Type[serializers.Serializer],
        error_codes: ErrorCodes = None,
    ):

        if not self.ticketing_system.api_key:
            raise Exception("Ticketing system doesn't define an API key.")

        logger.info(
            f"Ticketing system API call - POST {url} data: {json.dumps(payload)}"
        )

        response = requests.post(
            url,
            json=payload,
            timeout=self.TIMEOUT,
            auth=TokenAuth(self.ticketing_system.api_key),
        )

        return self._process_response(response, success_serializer, error_codes)

    @staticmethod
    def _process_response(
        response,
        success_serializer: Type[serializers.Serializer],
        error_codes: ErrorCodes = None,
    ):
        try:
            data = response.json()
            if 400 <= response.status_code <= 499:
                error_serializer = _build_error_serializer(error_codes or ())(data=data)
                error_serializer.is_valid(raise_exception=True)
                raise TicketingSystemRequestError(**error_serializer.data["error"])
            response.raise_for_status()
            many = getattr(success_serializer, "_many", False)
            serializer = success_serializer(data=data, many=many)
            serializer.is_valid(raise_exception=True)

        except (JSONDecodeError, serializers.ValidationError, RequestException) as e:
            raise TicketingSystemNotBehavingError(response=response) from e

        return serializer.validated_data
