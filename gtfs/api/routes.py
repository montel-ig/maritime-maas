from rest_framework import filters, serializers, viewsets

from gtfs.api.stops import StopSerializer
from gtfs.models import Route, Stop


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "name", "stops")

    name = serializers.SerializerMethodField()
    stops = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.short_name

    def get_stops(self, obj):
        if "stops" not in self.context:
            self.context["stops"] = Stop.objects.all()
        stops = self.context["stops"].filter(feed=obj.feed)
        return StopSerializer(stops, many=True).data


class RoutesByStopIdFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params

        if "stopId" not in query_params:
            return queryset

        stop_id = query_params["stopId"]
        stop = Stop.objects.get(pk=stop_id)
        queryset = queryset.filter(feed=stop.feed)
        return queryset


class RoutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [RoutesByStopIdFilterBackend]
