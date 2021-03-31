from django.contrib import admin

from gtfs.admin import FeedInline

from .models import MaasOperator, Permission, TicketingSystem, TransportServiceProvider


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 0


@admin.register(MaasOperator)
class MaasOperatorAdmin(admin.ModelAdmin):
    inlines = (PermissionInline,)


@admin.register(TransportServiceProvider)
class TransportServiceProviderAdmin(admin.ModelAdmin):
    inlines = (PermissionInline,)


@admin.register(TicketingSystem)
class TicketingSystemAdmin(admin.ModelAdmin):
    inlines = (FeedInline,)
