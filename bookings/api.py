from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bookings.models import Booking
from bookings.serializers import BookingSerializer, PassthroughParametersSerializer


@extend_schema_view(
    create=extend_schema(summary=_("Create a booking")),
    confirm=extend_schema(summary=_("Confirm a previously created booking")),
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
