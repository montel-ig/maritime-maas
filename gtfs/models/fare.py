from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .agency import Agency
from .base import GTFSModel


class Fare(GTFSModel):
    class PaymentMethod(models.IntegerChoices):
        ON_BOARD = 0, _("Fare is paid on board")
        BEFORE_BOARDING = 1, _("Fare must be paid before boarding")

    class Transfers(models.IntegerChoices):
        NO_TRANSFERS = 0, _("No transfers permitted on this fare")
        ONE_TRANSFER = 1, _("Passenger may transfer once")
        TWO_TRANSFERS = 2, _("Passenger may transfer twice")
        __empty__ = _("Unlimited transfers are permitted")

    agency = models.ForeignKey(
        Agency,
        verbose_name=_("agency"),
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        verbose_name=_("price"), max_digits=10, decimal_places=2
    )
    currency_type = models.CharField(
        max_length=3, help_text=_("ISO 4217 alphabetical currency code")
    )
    payment_method = models.PositiveSmallIntegerField(
        verbose_name=_("payment method"), choices=PaymentMethod.choices
    )
    transfers = models.PositiveSmallIntegerField(
        verbose_name=_("transfers"), choices=Transfers.choices, null=True
    )

    class Meta(GTFSModel.Meta):
        verbose_name = _("fare")
        verbose_name_plural = _("fares")
        default_related_name = "fares"

    def __str__(self):
        return f"{self.agency} | {self.price} {self.currency_type}"
