from django.contrib import admin

from .models import MaasOperator, Permission, TransportServiceProvider


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 0


@admin.register(MaasOperator)
class MaasOperatorAdmin(admin.ModelAdmin):
    inlines = (PermissionInline,)


@admin.register(TransportServiceProvider)
class TransportServiceProviderAdmin(admin.ModelAdmin):
    inlines = (PermissionInline,)
