from uuid import UUID, uuid5

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

API_ID_NAMESPACE = UUID("4d5d9db9-a18e-4e83-aeb9-369e32a966fd")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class PriceModel(models.Model):
    price = models.DecimalField(
        verbose_name=_("price"), max_digits=10, decimal_places=2
    )
    currency_type = models.CharField(
        verbose_name=_("currency type"),
        max_length=3,
        help_text=_("ISO 4217 alphabetical currency code"),
    )

    class Meta:
        abstract = True


class GTFSModel(models.Model):
    feed = models.ForeignKey("Feed", verbose_name=_("feed"), on_delete=models.CASCADE)

    class Meta:
        abstract = True


class GTFSModelWithSourceID(GTFSModel):
    source_id = models.CharField(verbose_name=_("source ID"), max_length=255)
    api_id = models.UUIDField(verbose_name=_("API ID"), unique=True)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["feed", "source_id"],
                name="unique_feed_%(app_label)s_%(class)s",
            )
        ]

    def populate_api_id(self):
        self.api_id = uuid5(
            API_ID_NAMESPACE,
            f"{self.__class__.__name__}:{self.feed_id}:{self.source_id}",
        )

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.populate_api_id()
        super().save(*args, **kwargs)
