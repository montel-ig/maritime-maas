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


class DepartureSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="api_id")
    short_name = serializers.CharField(source="trip.short_name")
    arrival_time = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    direction_id = serializers.IntegerField(source="trip.direction_id")
    departure_headsign = serializers.CharField(source="trip.headsign")
    stop_headsign = serializers.SerializerMethodField()
    stop_sequence = serializers.SerializerMethodField()
    wheelchair_accessible = serializers.IntegerField(
        source="trip.wheelchair_accessible"
    )
    bikes_allowed = serializers.IntegerField(source="trip.bikes_allowed")
    route_id = serializers.SlugRelatedField(
        source="trip.route", slug_field="api_id", read_only=True
    )
    block_id = serializers.CharField(source="trip.block_id")
    timepoint = serializers.SerializerMethodField()

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

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_arrival_time(self, obj):
        return obj.trip.stops_stop_times[0].get_arrival_time_datetime(obj)

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_departure_time(self, obj):
        return obj.trip.stops_stop_times[0].get_departure_time_datetime(obj)

    @extend_schema_field(OpenApiTypes.STR)
    def get_stop_headsign(self, obj):
        return obj.trip.stops_stop_times[0].stop_headsign

    @extend_schema_field(OpenApiTypes.INT)
    def get_stop_sequence(self, obj):
        return obj.trip.stops_stop_times[0].stop_sequence

    @extend_schema_field(OpenApiTypes.INT)
    def get_timepoint(self, obj):
        return obj.trip.stops_stop_times[0].timepoint


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

    @extend_schema_field(DepartureSerializer(many=True))
    def get_departures(self, obj):
        if "date" not in self.context:
            return None
        queryset = (
            Departure.objects.filter(
                trip__stop_times__stop=obj, date=self.context["date"]
            )
            .select_related("trip", "trip__route", "trip__route__agency")
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
        if "route_id" in self.context:
            queryset = queryset.filter(trip__route_id=self.context["route_id"])

        return DepartureSerializer(queryset, many=True, context=self.context).data


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
