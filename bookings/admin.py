from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "api_id",
        "maas_operator",
        "ticketing_system",
        "status",
        "created_at",
        "updated_at",
    )
