from rest_framework import serializers, viewsets
from rest_framework_gis.filters import DistanceToPointFilter

from gtfs.models import Stop


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ("id", "name", "coordinates")

    coordinates = serializers.SerializerMethodField()

    def get_coordinates(self, obj):
        if obj.point:
            return {"latitude": obj.point.y, "longitude": obj.point.x}


class RadiusToLocationFilter(DistanceToPointFilter):
    dist_param = "radius"
    point_param = "location"


class StopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    distance_filter_field = "point"
    filter_backends = [RadiusToLocationFilter]
    distance_filter_convert_meters = True
