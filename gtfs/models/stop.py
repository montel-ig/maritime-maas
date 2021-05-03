from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.managers import TranslatableQuerySet
from parler.models import TranslatableModel, TranslatedFields, TranslationDoesNotExist

from maas.models import MaasOperator

from .base import GTFSModelWithSourceID
from .feed import Feed


class StopQueryset(TranslatableQuerySet):
    def for_maas_operator(self, maas_operator: MaasOperator):
        feeds = Feed.objects.for_maas_operator(maas_operator)
        return self.filter(feed__in=feeds)


class Stop(TranslatableModel, GTFSModelWithSourceID):
    class WheelchairBoarding(models.IntegerChoices):
        UNKNOWN = 0, _("Unknown")
        POSSIBLE = 1, _("Possible")
        NOT_POSSIBLE = 2, _("Not possible")

    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255, blank=True),
        desc=models.TextField(verbose_name=_("description"), blank=True),
        tts_name=models.CharField(
            verbose_name=_("TTS name"),
            max_length=255,
            help_text=_("readable version of the name"),
            blank=True,
        ),
    )

    code = models.CharField(verbose_name=_("code"), max_length=255, blank=True)
    point = models.PointField(verbose_name=_("point"))
    wheelchair_boarding = models.PositiveSmallIntegerField(
        verbose_name=_("wheelchair boarding"),
        choices=WheelchairBoarding.choices,
        default=WheelchairBoarding.UNKNOWN,
    )

    objects = StopQueryset.as_manager()

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("stop")
        verbose_name_plural = _("stops")
        default_related_name = "stops"

    def __str__(self):
        try:
            return self.safe_translation_getter("name", any_language=True)
        except TranslationDoesNotExist:
            return super().__str__()
