from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ParseError


class BaseGTFSViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "api_id"

    # if set, query params given to the detail endpoint will be serialized by this
    # serializer and added to the context of the ViewSet's main serializer
    detail_query_params_serializer_class = None

    def get_queryset(self):
        maas_operator = self.request.user.maas_operator
        qs = super().get_queryset()
        return qs.for_maas_operator(maas_operator)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.detail_query_params_serializer_class and self.action == "retrieve":
            query_params_serializer = self.detail_query_params_serializer_class(
                data=context["request"].query_params
            )
            if not query_params_serializer.is_valid():
                raise ParseError(query_params_serializer.errors)

            for field, value in query_params_serializer.validated_data.items():
                context[field] = value

        return context


class NestedDepartureQueryParamsSerializer(serializers.Serializer):
    date = serializers.DateField(
        required=False, help_text=_("Sets the datetime to filter the departures.")
    )
    direction_id = serializers.IntegerField(
        min_value=0,
        max_value=1,
        required=False,
        help_text=_(
            "Filters departures of a stop by direction (0=outbound, 1=inbound)"
        ),
    )

    class Meta:
        fields = ("date", "direction_id")
