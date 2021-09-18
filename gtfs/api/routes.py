from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_field,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)
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
    name = serializers.CharField(source="long_name")
    stops = serializers.SerializerMethodField()
    agency = AgencySerializer(read_only=True)
    ticket_types = serializers.SerializerMethodField()
    description = serializers.CharField(source="desc")

    @extend_schema_field(StopSerializer(many=True))
    def get_stops(self, obj):
        stops = (
            Stop.objects.filter(stop_times__trip__route_id=obj.id)
            .distinct()
            .order_by("id")
        )
        return StopSerializer(
            stops, many=True, context=dict(**self.context, route_id=obj.id)
        ).data

    @extend_schema_field(FareSerializer(many=True))
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="stop_id",
                description=("The UUID of the stop"),
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "stop_id", value="1455cf8a-127e-4ad7-b662-74de2ab316cf"
                    )
                ],
            ),
        ],
        summary=_("List all routes"),
        tags=["Booking Options"],
        description=[
            "By default all the routes are returned. Routes can be filtered with"
            " `stop_id` to get only the routes that are including a specific stop."
            "In addition to basic information of the route also available ticket "
            "types and stops are returned by this endpoint."
        ],
    ),
    retrieve=extend_schema(
        summary=_("Retrieve a single route"),
        parameters=[
            NestedDepartureQueryParamsSerializer,
            OpenApiParameter(
                name="api_id",
                description=("The UUID of the route"),
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                examples=[
                    OpenApiExample("id", value="1455cf8a-127e-4ad7-b662-74de2ab316cf")
                ],
            ),
            OpenApiParameter(
                name="date",
                description=(
                    "Date to return departures for. Departures are returned "
                    "only for the given date. If date is not provided the "
                    "departures array won't be present in the response."
                ),
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                examples=[OpenApiExample("date", value="2021-01-01")],
            ),
            OpenApiParameter(
                name="direction_id",
                description=(
                    "Filters departures of a route by direction (0=outbound, "
                    "1=inbound). For more information about `direction_id` "
                    "please refer to the technical documentation."
                ),
                type=OpenApiTypes.INT,
                enum=[0, 1],
                location=OpenApiParameter.QUERY,
                examples=[OpenApiExample("direction_id", value=1)],
            ),
        ],
        tags=["Booking Options"],
        description=[
            "Returns the details of a single route requested by `UUID`. "
            "In addition to basic information of the route also available "
            "ticket types and stops are returned by this endpoint. By "
            " providing the `date` parameter this endpoint will also return "
            "the departures for the given date. It can be also used together "
            "with `direction_id` parameter which returns departures to "
            "certain direction (for example to filter out arriving inbound "
            "ferries and only show departing outbound departures)."
        ],
    ),
)
class RoutesViewSet(BaseGTFSViewSet):
    queryset = Route.objects.select_related("agency").order_by("sort_order", "id")
    serializer_class = RouteSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RouteFilter
    detail_query_params_serializer_class = NestedDepartureQueryParamsSerializer
