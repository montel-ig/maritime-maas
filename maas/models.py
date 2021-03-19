import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _


class MaasOperator(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=64)
    transport_service_providers = models.ManyToManyField(
        "TransportServiceProvider", related_name="maas_operators", through="Permission"
    )
    api_token = models.CharField(
        _("api_token"), blank=True, max_length=100, db_index=True
    )

    class Meta:
        verbose_name = _("maas operator")
        verbose_name_plural = _("maas operators")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.api_token = self.generate_api_token()
        return super().save(*args, **kwargs)

    def generate_api_token(self):
        return secrets.token_urlsafe(64)[:100]


class TransportServiceProvider(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=64)

    class Meta:
        verbose_name = _("transport service provider")
        verbose_name_plural = _("transport service provider")

    def __str__(self):
        return self.name


class Permission(models.Model):
    maas_operator = models.ForeignKey(MaasOperator, on_delete=models.CASCADE)
    transport_service_provider = models.ForeignKey(
        TransportServiceProvider, on_delete=models.CASCADE
    )
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        default_related_name = "permissions"

    def __str__(self):
        return f"{self.maas_operator.name} - {self.transport_service_provider.name}"
