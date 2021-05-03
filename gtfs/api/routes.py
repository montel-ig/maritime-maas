from django_filters import rest_framework as filters
from rest_framework import serializers

from gtfs.api.base import BaseGTFSViewSet, NestedDepartureQueryParamsSerializer
from gtfs.api.stops import StopSerializer
from gtfs.models import Agency, Fare, FareRiderCategory, Route, Stop


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ("name", "url", "logo_url", "phone", "email")


class FareRiderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FareRiderCategory
        fields = ("id", "name", "description", "price", "currency_type")

    id = serializers.UUIDField(source="rider_category.api_id")
    name = serializers.CharField(source="rider_category.name")
    description = serializers.CharField(source="rider_category.description")


class FareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fare
        fields = ("id", "name", "description", "instructions", "customer_types")

    id = serializers.UUIDField(source="api_id")
    customer_types = FareRiderCategorySerializer(
        source="fare_rider_categories", many=True
    )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "name",
            "stops",
            "agency",
            "ticket_types",
            "capacity_sales",
            "url",
            "description",
        )

    id = serializers.UUIDField(source="api_id")
    name = serializers.CharField(source="short_name")
    stops = serializers.SerializerMethodField()
    agency = AgencySerializer(read_only=True)
    ticket_types = serializers.SerializerMethodField()
    description = serializers.CharField(source="desc")

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

    def get_ticket_types(self, obj):
        ticket_types = (
            Fare.objects.filter(fare_rules__route_id=obj.id)
            .distinct()
            .prefetch_related(
                "fare_rider_categories", "fare_rider_categories__rider_category"
            )
        )
        return FareSerializer(ticket_types, many=True, context=self.context).data


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
