import base64
import datetime
import sys
import uuid
from decimal import Decimal
from pathlib import PurePath

from django.utils import timezone
from django.utils.translation import get_language

from bookings.models import Booking
from gtfs.models import Departure, FareRiderCategory, Route


def format_timestamp(d: datetime.datetime):
    return f"{d.replace(tzinfo=None).isoformat()}Z"


def get_reservation_data() -> dict:
    return {"id": str(uuid.uuid4()), "status": "RESERVED"}


def format_price(price: Decimal) -> str:
    return str(price.quantize(Decimal(10) ** -2))


def get_translated_field(obj, field):
    return obj.safe_translation_getter(field, any_language=True) or ""


def get_confirmations_data(pk, include_qr=True) -> dict:
    if "pytest" in sys.modules:
        return get_test_confirmations_data(pk, include_qr)
    else:
        return get_actual_confirmations_data(pk, include_qr)


def get_test_confirmations_data(pk, include_qr=True) -> dict:
    if include_qr:
        path = PurePath(__file__).parent.joinpath("data", "ticket_qr.png")
        with open(path.as_posix(), "rb") as f:
            ticket = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    else:
        ticket = "QR_CODE"
    valid_from = timezone.now()
    departed_at = valid_from + datetime.timedelta(hours=1)
    valid_to = valid_from + datetime.timedelta(days=1)
    return {
        "id": pk,
        "status": "CONFIRMED",
        "tickets": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "qr_code": ticket,
                "departures": [
                    {
                        "from": "Kauppatori",
                        "to": "Vallisaari",
                        "depart_at": format_timestamp(departed_at),
                    }
                ],
                "name": "Day in Vallisaari",
                "description": "This is the description of the ticket",
                "instructions": "These are the instructions of the ticket",
                "agency": {
                    "name": "MaaS Line",
                    "logo_url": "http://www.agency.com/logo.png",
                },
                "ticket_html": "<div>...</div>",
                "ticket_type": "Päivälippu",
                "customer_type": "Aikuinen",
                "amount": 12,
                "currency": "EUR",
                "terms_of_use": "http://www.terms.and.conditions.fi",
                "locale": "fi",
                "valid_from": format_timestamp(valid_from),
                "valid_to": format_timestamp(valid_to),
                "refresh_at": format_timestamp(valid_to),
            }
        ],
    }


def get_actual_confirmations_data(pk, include_qr=True) -> dict:
    if include_qr:
        path = PurePath(__file__).parent.joinpath("data", "ticket_qr.png")
        with open(path.as_posix(), "rb") as f:
            ticket = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    else:
        ticket = "QR_CODE"

    valid_from = timezone.now()
    vat = Decimal("0.24")

    booking = Booking.objects.get(source_id=pk)
    feed = booking.ticketing_system.feeds.first()
    route = Route.objects.get(translations__long_name=booking.route_name, feed=feed)
    agency = route.agency
    departure = Departure.objects.filter(trip__route=route).first()
    from_stop_time = departure.trip.stop_times.order_by("stop_sequence").first()
    to_stop_time = departure.trip.stop_times.order_by("stop_sequence").last()
    fare = route.fares.first()
    rider_category = fare.rider_categories.first()
    block_ids = route.trips.values_list("block_id", flat=True).distinct()

    return {
        "id": pk,
        "status": "CONFIRMED",
        "tickets": [
            {
                "id": uuid.uuid4(),
                "agency": {
                    "name": get_translated_field(agency, "name"),
                    "logo_url": agency.logo_url,
                },
                "customer_type": {
                    "description": get_translated_field(rider_category, "description"),
                    "name": get_translated_field(rider_category, "name"),
                },
                "locale": get_language(),
                "maas_operator_id": booking.maas_operator.identifier,
                "price": {
                    "amount_excluding_vat": format_price(
                        FareRiderCategory.objects.get(
                            fare=fare, rider_category=rider_category
                        ).price
                        / (1 + vat)
                    ),
                    "amount_total": format_price(fare.price),
                    "currency": "EUR",
                    "vat_amount": format_price(fare.price - fare.price / (1 + vat)),
                    "vat_percentage": str(int(vat * 100)),
                },
                "qr_code": ticket,
                "route": {
                    "name": get_translated_field(route, "long_name")
                    or get_translated_field(route, "short_name"),
                    "description": get_translated_field(route, "desc"),
                    # yes, I know
                    "legs": sorted(
                        [
                            {
                                "stops": [
                                    {
                                        "location": {
                                            "lat": stop_time.stop.point[1],
                                            "lon": stop_time.stop.point[0],
                                        },
                                        "name": get_translated_field(
                                            stop_time.stop, "name"
                                        ),
                                        "stop_time": format_timestamp(
                                            stop_time.get_departure_time_datetime(
                                                departure
                                            )
                                        ),
                                    }
                                    for stop_time in route.trips.filter(
                                        block_id=block_id
                                    )
                                    .first()
                                    .stop_times.order_by("stop_sequence")
                                ]
                            }
                            for block_id in block_ids
                        ],
                        key=lambda x: next(iter(x["stops"]), {}).get(
                            "stop_time", datetime.datetime.max
                        ),
                    ),
                },
                "terms_url": "http://www.terms.and.conditions.fi",  # TODO
                "departures": [
                    {
                        "from": get_translated_field(from_stop_time.stop, "name"),
                        "to": get_translated_field(to_stop_time.stop, "name"),
                        "depart_at": format_timestamp(
                            from_stop_time.get_departure_time_datetime(departure)
                        ),
                    }
                ],
                "schema_version": 2,
                "ticket_type": {
                    "name": get_translated_field(fare, "name"),
                    "description": get_translated_field(fare, "description"),
                    "instructions": get_translated_field(fare, "instructions"),
                },
                "validity": {"starts_at": format_timestamp(valid_from)},
            }
            for _ in range(booking.ticket_count)
        ],
    }
