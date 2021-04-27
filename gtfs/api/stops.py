from datetime import datetime, timezone

from django.db.models import Prefetch
from rest_framework import serializers
from rest_framework_gis.filters import DistanceToPointFilter

from gtfs.models import Stop, StopTime
from gtfs.models.departure import Departure

from .base import BaseGTFSViewSet, NestedDepartureQueryParamsSerializer


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
    stop_timepoint = serializers.SerializerMethodField()
    route_id = serializers.SlugRelatedField(
        source="trip.route", slug_field="api_id", read_only=True
    )
    block_id = serializers.CharField(source="trip.block_id")

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
            "stop_timepoint",
            "route_id",
            "block_id",
        )

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get("route_id"):
            del fields["route_id"]
        return fields

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

    def get_stop_timepoint(self, obj):
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
        )

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
        if "route_id" in self.context:
            queryset = queryset.filter(trip__route_id=self.context["route_id"])

        return DepartureSerializer(queryset, many=True, context=self.context).data


class RadiusToLocationFilter(DistanceToPointFilter):
    dist_param = "radius"
    point_param = "location"


class StopViewSet(BaseGTFSViewSet):
    queryset = Stop.objects.order_by("id")

    serializer_class = StopSerializer
    distance_filter_field = "point"
    filter_backends = [RadiusToLocationFilter]
    distance_filter_convert_meters = True
    detail_query_params_serializer_class = NestedDepartureQueryParamsSerializer
