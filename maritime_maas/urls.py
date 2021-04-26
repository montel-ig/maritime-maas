from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework import routers

from bookings.api import BookingViewSet
from gtfs.api.routes import RoutesViewSet
from gtfs.api.shapes import ShapeViewSet
from gtfs.api.stops import StopViewSet
from mock_ticket_api.api import MockTicketViewSet

router = routers.DefaultRouter()
router.register(r"routes", RoutesViewSet, basename="routes")
router.register(r"stops", StopViewSet, basename="stops")
router.register(r"bookings", BookingViewSet, basename="bookings")
router.register(r"shapes", ShapeViewSet, basename="shapes")

if settings.MOCK_TICKETING_API:
    router.register(r"mock_ticket", MockTicketViewSet, basename="mockapi")

urlpatterns = [path("admin/", admin.site.urls), path("v1/", include(router.urls))]


#
# Kubernetes liveness & readiness probes
#
def healthz(*args, **kwargs):
    return HttpResponse(status=200)


def readiness(*args, **kwargs):
    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
