from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bookings.models import Booking
from gtfs.models import Departure, RiderCategory, Route


def get_object_by_api_id(qs, api_id):
    try:
        return qs.get(api_id=api_id)
    except ObjectDoesNotExist:
        raise ValidationError(
            f'Invalid ID "{api_id}" - object does not exist.', code="does_not_exist"
        )


class TicketSerializer(serializers.Serializer):
    ticket_type_id = serializers.UUIDField()
    customer_type_id = serializers.UUIDField()

    def validate_ticket_type_id(self, value):
        if "route" not in self.parent.parent.context:
            return None
        self.context["fare"] = get_object_by_api_id(
            self.parent.parent.context["route"].fares.all(), value
        )
        return self.context["fare"]

    def validate_customer_type_id(self, value):
        if "fare" not in self.context:
            return
        return get_object_by_api_id(
            RiderCategory.objects.filter(fares=self.context["fare"]),
            value,
        )

    def validate(self, data):
        data["fare"] = data.pop("ticket_type_id", None)
        data["fare_rider_category"] = data.pop("customer_type_id", None)
        return data


class BookingSerializer(serializers.ModelSerializer):
    route_id = serializers.UUIDField(required=False, write_only=True)
    departure_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=False,
        write_only=True,
    )
    tickets = TicketSerializer(many=True, write_only=True)
    locale = serializers.ChoiceField(
        choices=("fi", "sv", "en"), required=False, write_only=True
    )
    id = serializers.UUIDField(source="api_id", read_only=True)

    class Meta:
        model = Booking
        fields = ("route_id", "departure_ids", "tickets", "locale", "id", "status")
        read_only_fields = ("id", "status")

    def validate_route_id(self, value):
        self.context["route"] = get_object_by_api_id(
            Route.objects.for_maas_operator(self.context["request"].user.maas_operator),
            value,
        )
        return self.context["route"]

    def validate_departure_ids(self, values):
        departures = [
            get_object_by_api_id(
                Departure.objects.for_maas_operator(
                    self.context["request"].user.maas_operator
                ),
                departure_id,
            )
            for departure_id in values
        ]

        if "route" not in self.context:
            self.context["route"] = departures[0].trip.route

        if not all(d.trip.route == self.context["route"] for d in departures):
            raise ValidationError(
                "All departures must belong to the same route.",
                code="invalid_departures",
            )

        return departures

    def validate(self, data):
        data["route"] = data.pop("route_id", self.context["route"])
        data["departures"] = data.pop("departure_ids", [])
        return data

    def create(self, validated_data):
        return Booking.objects.create_reservation(
            self.context["request"].user.maas_operator,
            self.validated_data["route"].feed.ticketing_system,
        )


class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = BookingSerializer
    lookup_field = "api_id"

    def get_queryset(self):
        return Booking.objects.for_maas_operator(self.request.user.maas_operator)

    @action(detail=True, methods=["post"])
    def confirm(self, request, api_id=None):
        booking = self.get_object()
        booking.confirm()
        return Response(self.serializer_class(instance=booking).data)
