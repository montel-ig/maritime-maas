from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_array_type, build_basic_type
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_serializer,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import serializers

from gtfs.api.base import BaseGTFSViewSet, NestedDepartureQueryParamsSerializer
from gtfs.models.shape import Shape

LINESTRING_GEOMETRY = {
    "type": "object",
    "properties": {
        "type": {
            "description": _("The type of the geos instance"),
            "type": "string",
            "enum": ["LineString"],
        },
        "coordinates": build_array_type(
            build_array_type(build_basic_type(float), min_length=2), min_length=2
        ),
    },
    "required": ["type", "coordinates"],
}


class LineStringFieldExtension(OpenApiSerializerFieldExtension):
    """OpenApiSerializerField for a linestring geometry.

    Adapted from https://github.com/tfranzel/drf-spectacular/pull/38/files
    """

    target_class = "rest_framework_gis.fields.GeometryField"

    def map_serializer_field(self, auto_schema, direction):
        return LINESTRING_GEOMETRY


@extend_schema_serializer()
class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = ("id", "geometry")

    id = serializers.UUIDField(source="api_id")


class ShapeFilter(filters.FilterSet):
    route_id = filters.UUIDFilter(field_name="trips__route__api_id", distinct=True)
    departure_id = filters.UUIDFilter(
        field_name="trips__departures__api_id", distinct=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not any(f in kwargs["data"] for f in ("route_id", "departure_id")):
            self.form.add_error(
                None, 'Either "route_id" or "departure_id" is required.'
            )

    class Meta:
        model: Shape
        fields = ("route_id", "departure_id")


@extend_schema_view(
    list=extend_schema(
        summary=_("List all shapes"),
        parameters=[
            OpenApiParameter(
                name="departure_id",
                description=("The UUID of the departure"),
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "departure_id", value="1455cf8a-127e-4ad7-b662-74de2ab316cf"
                    )
                ],
            ),
            OpenApiParameter(
                name="route_id",
                description=("The UUID of the route"),
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "route_id", value="1455cf8a-127e-4ad7-b662-74de2ab316cf"
                    )
                ],
            ),
        ],
        tags=["Booking Options"],
        description=[
            "Return the path that vehicle travels along a route in a sequence "
            "of points (latitude and longitude). Shapes can be filtered with "
            "by departure with `departure_id` or by route with `route_id` "
            "parameter."
        ],
    ),
    retrieve=extend_schema(
        summary=_("Retrieve a single shape"),
        parameters=[ShapeSerializer],
        tags=["Booking Options"],
    ),
)
class ShapeViewSet(BaseGTFSViewSet):
    queryset = Shape.objects.all()
    serializer_class = ShapeSerializer
    detail_query_params_serializer_class = NestedDepartureQueryParamsSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ShapeFilter
