from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from maas.models import MaasOperator

from .base import GTFSModel


class FeedQueryset(models.QuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        return self.filter(
            ticketing_system__transport_service_providers__maas_operators=maas_operator
        )


class Feed(models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
        blank=True,
        help_text=_(
            "If left empty, will be autopopulated with the feed info's publisher name when one is available."
        ),
    )
    url_or_path = models.CharField(verbose_name=_("URL"), max_length=255)
    imported_at = models.DateTimeField(
        verbose_name=_("imported at"), null=True, blank=True
    )
    import_attempted_at = models.DateTimeField(
        verbose_name=_("import attempted at"), null=True, blank=True
    )
    last_import_error_message = models.TextField(
        verbose_name=_("error message"), blank=True
    )

    ticketing_system = models.ForeignKey(
        "maas.TicketingSystem",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("ticketing system"),
    )
    fingerprint = models.CharField(
        verbose_name=_("fingerprint"),
        max_length=255,
        blank=True,
        help_text=_(
            "This value will be used to determine if the feed should be updated."
        ),
    )

    objects = FeedQueryset.as_manager()

    class Meta:
        verbose_name = _("feed")
        verbose_name_plural = _("feeds")
        default_related_name = "feeds"

    def save(self, *args, **kwargs):
        if not self.name and hasattr(self, "feed_info"):
            self.name = self.feed_info.publisher_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.url_or_path

    @property
    def last_import_successful(self):
        return (
            not bool(self.last_import_error_message)
            if self.import_attempted_at
            else None
        )


class FeedInfo(GTFSModel):
    feed = models.OneToOneField(
        Feed, verbose_name=_("feed"), related_name="feed_info", on_delete=models.CASCADE
    )
    publisher_name = models.CharField(verbose_name=_("publisher name"), max_length=255)
    publisher_url = models.URLField(verbose_name=_("publisher URL"))
    lang = models.CharField(
        verbose_name=_("language"),
        max_length=16,
        help_text=_(
            "Default language for the text in this dataset. Used by the feed importer. "
            "IETF BCP 47 language code"
        ),
    )
    default_lang = models.CharField(
        verbose_name=_("default language"),
        blank=True,
        max_length=16,
        help_text=_(
            "Defines the language used when the data consumer doesn’t know the language of the rider. "
            "IETF BCP 47 language code"
        ),
    )
    start_date = models.DateField(verbose_name=_("start date"), blank=True, null=True)
    end_date = models.DateField(verbose_name=_("end date"), blank=True, null=True)
    version = models.CharField(verbose_name=_("version"), max_length=64, blank=True)
    contact_email = models.EmailField(verbose_name=_("contact email"), blank=True)

    class Meta:
        verbose_name = _("feed info")
        verbose_name_plural = _("feed info")

    def __str__(self):
        return f"{self.feed} info version {self.version or 'N/A'}"
