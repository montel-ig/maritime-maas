from django_filters import rest_framework as filters
from rest_framework import serializers

from gtfs.api.base import BaseGTFSViewSet, NestedDepartureQueryParamsSerializer
from gtfs.models.shape import Shape


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


class ShapeViewSet(BaseGTFSViewSet):
    queryset = Shape.objects.all()
    serializer_class = ShapeSerializer
    detail_query_params_serializer_class = NestedDepartureQueryParamsSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ShapeFilter
