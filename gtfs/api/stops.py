from datetime import datetime, timezone

from django.db.models import Prefetch
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ParseError
from rest_framework_gis.filters import DistanceToPointFilter

from gtfs.models import Stop, StopTime
from gtfs.models.departure import Departure


class DepartureSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="api_id")
    short_name = serializers.CharField(source="trip.short_name")
    arrival_time = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    direction_id = serializers.IntegerField(source="trip.direction_id")
    departure_headsign = serializers.CharField(source="trip.headsign")
    stop_headsign = serializers.SerializerMethodField()
    stop_sequence = serializers.SerializerMethodField()
    route_id = serializers.SlugRelatedField(
        source="trip.route", slug_field="api_id", read_only=True
    )

    class Meta:
        model = Departure
        fields = (
            "id",
            "short_name",
            "arrival_time",
            "departure_time",
            "direction_id",
            "departure_headsign",
            "stop_headsign",
            "stop_sequence",
            "route_id",
        )

    def get_arrival_time(self, obj):
        return datetime.combine(
            obj.date, obj.trip.stops_stop_times[0].arrival_time, tzinfo=timezone.utc
        )

    def get_departure_time(self, obj):
        return datetime.combine(
            obj.date, obj.trip.stops_stop_times[0].departure_time, tzinfo=timezone.utc
        )

    def get_stop_headsign(self, obj):
        return obj.trip.stops_stop_times[0].stop_headsign

    def get_stop_sequence(self, obj):
        return obj.trip.stops_stop_times[0].stop_sequence


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ("id", "name", "coordinates", "departures")

    id = serializers.UUIDField(source="api_id")
    coordinates = serializers.SerializerMethodField()
    departures = serializers.SerializerMethodField()

    def get_fields(self):
        fields = super().get_fields()
        if "date" not in self.context:
            del fields["departures"]
        return fields

    def get_coordinates(self, obj):
        if obj.point:
            return {"latitude": obj.point.y, "longitude": obj.point.x}

    def get_departures(self, obj):
        queryset = (
            Departure.objects.filter(
                trip__stop_times__stop=obj, date=self.context["date"]
            )
            .select_related("trip", "trip__route")
            .prefetch_related(
                Prefetch(
                    "trip__stop_times",
                    queryset=StopTime.objects.filter(stop=obj),
                    to_attr="stops_stop_times",
                ),
            )
            .order_by("trip__stop_times__departure_time")
        )
        if "direction_id" in self.context:
            queryset = queryset.filter(trip__direction_id=self.context["direction_id"])

        return DepartureSerializer(queryset, many=True, context=self.context).data


class RadiusToLocationFilter(DistanceToPointFilter):
    dist_param = "radius"
    point_param = "location"


class QueryParamsSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    direction_id = serializers.IntegerField(min_value=0, max_value=1, required=False)

    class Meta:
        fields = ("date", "direction_id")


class StopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stop.objects.all()

    serializer_class = StopSerializer
    distance_filter_field = "point"
    filter_backends = [RadiusToLocationFilter]
    distance_filter_convert_meters = True
    lookup_field = "api_id"

    def get_queryset(self):
        maas_operator = self.request.user.maas_operator
        qs = super().get_queryset()
        return qs.for_maas_operator(maas_operator)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "retrieve":
            filters_serializer = QueryParamsSerializer(
                data=context["request"].query_params
            )
            if not filters_serializer.is_valid():
                raise ParseError(filters_serializer.errors)

            for field, value in filters_serializer.validated_data.items():
                context[field] = value

        return context
