from django_filters import rest_framework as filters
from rest_framework import serializers, viewsets

from gtfs.api.stops import StopSerializer
from gtfs.models import Route, Stop


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "name", "stops")

    id = serializers.UUIDField(source="api_id")
    name = serializers.CharField(source="short_name")
    stops = serializers.SerializerMethodField()

    def get_stops(self, obj):
        stops = Stop.objects.filter(stop_times__trip__route_id=obj.id).distinct()
        return StopSerializer(stops, many=True).data


class RouteFilter(filters.FilterSet):
    stop_id = filters.UUIDFilter(field_name="trips__stop_times__stop__api_id")

    class Meta:
        model: Route
        fields = "stop_id"


class RoutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RouteFilter
    lookup_field = "api_id"

    def get_queryset(self):
        maas_operator = self.request.user.maas_operator
        qs = super().get_queryset()
        return qs.for_maas_operator(maas_operator)
