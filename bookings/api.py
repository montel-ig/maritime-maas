from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bookings.models import Booking
from bookings.serializers import BookingSerializer, PassthroughParametersSerializer


@extend_schema_view(
    create=extend_schema(
        summary=_("Create a booking"),
        tags=["Bookings"],
        description=[
            "Creates a new booking with given parameters. Route is defined "
            "by `route_id`. Departures must be given as route's "
            "`capacity_sales` field defines (for example if "
            "`capacity_sales=2` a departure must be selected for each leg). "
            "It's possible to make a booking with multiple tickets at a time "
            "and those `ticket_type_id` and `customer_type_id` combinations "
            "must be defined in the `tickets` parameter. `locale` sets the "
            "language for the actual ticket payload. `request_id` is an "
            "identifier for each request and `transaction_id` is an "
            "identifier for each create booking/confirm booking transaction. "
            "Both of the values can be used in debugging (especially when "
            "MaaS Operator is directly in touch with Transport Service "
            "Provider and cannot access the API logs). As a result the "
            "booking id and the state `CONFIRMED` is returned in case of "
            "successful booking. Otherwise error is returned (with details "
            "if possible)."
        ],
    ),
    confirm=extend_schema(
        summary=_("Confirm a previously created booking"),
        tags=["Bookings"],
        description=[
            "Confirms a previously created booking and returns the ticket "
            "payload in the response. Otherwise error is returned with "
            "possible details."
        ],
    ),
)
class BookingViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Booking.objects.none()  # Empty queryset for drf_spectacular
    serializer_class = BookingSerializer
    lookup_field = "api_id"

    def get_queryset(self):
        return Booking.objects.for_maas_operator(self.request.user.maas_operator)

    @action(detail=True, methods=["post"])
    def confirm(self, request, api_id=None):
        booking = self.get_object()

        passthrough_parameters = PassthroughParametersSerializer(data=request.data)
        passthrough_parameters.is_valid(raise_exception=True)
        tickets = booking.confirm(passthrough_parameters.validated_data)

        booking_data = self.serializer_class(instance=booking).data
        booking_data["tickets"] = tickets

        return Response(booking_data)
