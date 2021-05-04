from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .agency import Agency
from .base import GTFSModelWithSourceID, PriceModel


class Fare(TranslatableModel, GTFSModelWithSourceID, PriceModel):
    class PaymentMethod(models.IntegerChoices):
        ON_BOARD = 0, _("Fare is paid on board")
        BEFORE_BOARDING = 1, _("Fare must be paid before boarding")

    class Transfers(models.IntegerChoices):
        NO_TRANSFERS = 0, _("No transfers permitted on this fare")
        ONE_TRANSFER = 1, _("Passenger may transfer once")
        TWO_TRANSFERS = 2, _("Passenger may transfer twice")
        __empty__ = _("Unlimited transfers are permitted")

    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255, blank=True),
        description=models.CharField(
            verbose_name=_("description"), max_length=255, blank=True
        ),
        instructions=models.TextField(verbose_name=_("instructions"), blank=True),
    )
    agency = models.ForeignKey(
        Agency,
        verbose_name=_("agency"),
        on_delete=models.CASCADE,
    )
    payment_method = models.PositiveSmallIntegerField(
        verbose_name=_("payment method"), choices=PaymentMethod.choices
    )
    transfers = models.PositiveSmallIntegerField(
        verbose_name=_("transfers"), choices=Transfers.choices, null=True
    )
    routes = models.ManyToManyField(
        "Route", verbose_name=_("routes"), through="FareRule", blank=True
    )

    class Meta(GTFSModelWithSourceID.Meta):
        verbose_name = _("fare")
        verbose_name_plural = _("fares")
        default_related_name = "fares"

    def __str__(self):
        return f"{self.agency} | {self.price} {self.currency_type}"
