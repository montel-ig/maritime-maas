from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from rest_framework import exceptions, filters, serializers, viewsets

from gtfs.models import Stop


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ("id", "name", "coordinates")

    coordinates = serializers.SerializerMethodField()

    def get_coordinates(self, obj):
        if obj.point:
            return {"latitude": obj.point.x, "longitude": obj.point.y}


class LocationFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params

        if "location" not in query_params and "radius" not in query_params:
            return queryset

        try:
            location_points = query_params["location"].split(",")
            lat = float(location_points[0])
            lon = float(location_points[1])
            radius = int(query_params["radius"])
        except ValueError:
            raise exceptions.ParseError(
                "'location' values must be floats and radius an integer"
            )

        location = Point(lat, lon, srid=4326)

        queryset = queryset.annotate(distance=Distance("point", location))
        queryset = queryset.filter(distance__lte=radius)
        return queryset


class StopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    filter_backends = [LocationFilterBackend]
