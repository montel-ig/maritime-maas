from django.conf import settings
from rest_framework import routers
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from gtfs.api.routes import RoutesViewSet
from gtfs.api.stops import StopViewSet

router = routers.DefaultRouter()
router.register(r"routes", RoutesViewSet, basename="routes")
router.register(r"stops", StopViewSet, basename="stops")


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
