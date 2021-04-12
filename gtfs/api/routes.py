from django_filters import rest_framework as filters
from rest_framework import serializers

from gtfs.api.base import BaseGTFSViewSet, NestedDepartureQueryParamsSerializer
from gtfs.api.stops import StopSerializer
from gtfs.models import Agency, Route, Stop


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ("name", "url", "logo_url")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "name", "stops", "agency")

    id = serializers.UUIDField(source="api_id")
    name = serializers.CharField(source="short_name")
    stops = serializers.SerializerMethodField()
    agency = AgencySerializer(read_only=True)

    def get_stops(self, obj):
        stops = (
            Stop.objects.filter(stop_times__trip__route_id=obj.id)
            .distinct()
            .order_by("id")
        )
        return StopSerializer(
            stops,
            many=True,
            context=dict(**self.context, route_id=obj.id),
        ).data


class RouteFilter(filters.FilterSet):
    stop_id = filters.UUIDFilter(
        field_name="trips__stop_times__stop__api_id", distinct=True
    )

    class Meta:
        model: Route
        fields = "stop_id"


class RoutesViewSet(BaseGTFSViewSet):
    queryset = Route.objects.select_related("agency").order_by("sort_order", "id")
    serializer_class = RouteSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RouteFilter
    detail_query_params_serializer_class = NestedDepartureQueryParamsSerializer
