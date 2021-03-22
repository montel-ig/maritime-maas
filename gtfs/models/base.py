from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class GTFSModel(models.Model):
    feed = models.ForeignKey("Feed", verbose_name=_("feed"), on_delete=models.CASCADE)

    class Meta:
        abstract = True


class GTFSModelWithSourceID(GTFSModel):
    source_id = models.CharField(verbose_name=_("source ID"), max_length=255)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["feed", "source_id"],
                name="unique_feed_%(app_label)s_%(class)s",
            )
        ]
