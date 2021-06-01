from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_field, extend_schema_view
from rest_framework import serializers
from rest_framework_gis.filters import DistanceToPointFilter

from gtfs.models import Stop, StopTime
from gtfs.models.departure import Departure

from .base import BaseGTFSViewSet, NestedDepartureQueryParamsSerializer


class CoordinateSerializer(serializers.Serializer):
    latitude = serializers.FloatField(source="point.y", read_only=True)
    longitude = serializers.FloatField(source="point.x", read_only=True)


class StopTimeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    short_name = serializers.CharField(source="trip.short_name")
    arrival_time = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    direction_id = serializers.IntegerField(source="trip.direction_id")
    departure_headsign = serializers.CharField(source="trip.headsign")
    stop_headsign = serializers.CharField()
    stop_sequence = serializers.IntegerField()
    wheelchair_accessible = serializers.IntegerField(
        source="trip.wheelchair_accessible"
    )
    bikes_allowed = serializers.IntegerField(source="trip.bikes_allowed")
    route_id = serializers.SlugRelatedField(
        source="trip.route", slug_field="api_id", read_only=True
    )
    block_id = serializers.CharField(source="trip.block_id")
    timepoint = serializers.IntegerField()

    class Meta:
        model = StopTime
        fields = (
            "id",
            "short_name",
            "arrival_time",
            "departure_time",
            "direction_id",
            "departure_headsign",
            "stop_headsign",
            "stop_sequence",
            "wheelchair_accessible",
            "bikes_allowed",
            "route_id",
            "block_id",
            "timepoint",
        )

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get("route_id"):
            del fields["route_id"]
        return fields

    @extend_schema_field(OpenApiTypes.UUID)
    def get_id(self, obj):
        departure = obj.trip.dates_departure[0]
        return departure.api_id

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_arrival_time(self, obj):
        departure = obj.trip.dates_departure[0]
        return obj.get_arrival_time_datetime(departure)

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_departure_time(self, obj):
        departure = obj.trip.dates_departure[0]
        return obj.get_departure_time_datetime(departure)


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = (
            "id",
            "name",
            "coordinates",
            "departures",
            "tts_name",
            "wheelchair_boarding",
            "description",
        )

    id = serializers.UUIDField(source="api_id")
    coordinates = serializers.SerializerMethodField()
    departures = serializers.SerializerMethodField()
    description = serializers.CharField(source="desc")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["departures"] is None:
            del ret["departures"]
        return ret

    @extend_schema_field(CoordinateSerializer)
    def get_coordinates(self, obj):
        if obj.point:
            return CoordinateSerializer(obj).data

    @extend_schema_field(StopTimeSerializer(many=True))
    def get_departures(self, obj):
        if "date" not in self.context:
            return None

        queryset = (
            StopTime.objects.filter(
                stop=obj, trip__departures__date=self.context["date"]
            )
            .select_related("trip", "trip__route", "trip__route__agency")
            .prefetch_related(
                Prefetch(
                    "trip__departures",
                    queryset=Departure.objects.filter(
                        date=self.context["date"], trip__stop_times__stop=obj
                    ),
                    to_attr="dates_departure",
                )
            )
            .order_by("departure_time")
        )
        if "direction_id" in self.context:
            queryset = queryset.filter(trip__direction_id=self.context["direction_id"])
        if "route_id" in self.context:
            queryset = queryset.filter(trip__route_id=self.context["route_id"])

        return StopTimeSerializer(queryset, many=True, context=self.context).data


class RadiusToLocationFilter(DistanceToPointFilter):
    dist_param = "radius"
    point_param = "location"


@extend_schema_view(
    list=extend_schema(summary=_("List all stops")),
    retrieve=extend_schema(
        summary=_("Retrieve a single stop"),
        parameters=[NestedDepartureQueryParamsSerializer],
    ),
)
class StopViewSet(BaseGTFSViewSet):
    queryset = Stop.objects.order_by("id")

    serializer_class = StopSerializer
    distance_filter_field = "point"
    filter_backends = [RadiusToLocationFilter]
    distance_filter_convert_meters = True
    detail_query_params_serializer_class = NestedDepartureQueryParamsSerializer
