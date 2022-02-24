import base64
import datetime
import uuid
from pathlib import PurePath

from django.utils import timezone

from bookings.models import Booking
from gtfs.models import Route


def format_timestamp(d: datetime.datetime):
    return f"{d.replace(tzinfo=None).isoformat()}Z"


def get_reservation_data() -> dict:
    return {"id": str(uuid.uuid4()), "status": "RESERVED"}


def get_confirmations_data(pk, old_pk=None, include_qr=True) -> dict:
    if include_qr:
        qr_path = PurePath(__file__).parent.joinpath("data", "ticket_qr.png")
        with open(qr_path.as_posix(), "rb") as f:
            ticket = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        agency_path = PurePath(__file__).parent.joinpath(
            "data", "ticket_agency_image.png"
        )
        with open(agency_path.as_posix(), "rb") as f:
            agency_image = (
                f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            )
    else:
        ticket = "QR_CODE"
        agency_image = "AGENCY_IMAGE"
    valid_from = timezone.now()
    departed_at = valid_from + datetime.timedelta(hours=1)
    valid_to = valid_from + datetime.timedelta(days=1)
    route = {
        "description": "Nice scenic route from Kauppatori to Korkeasaari",
        "name": "Kauppatori - Korkeasaari",
    }

    # Check if route has capacity sales enabled to make data more realistic
    try:
        booking = Booking.objects.get(source_id=old_pk or pk)
        if Route.objects.filter(
            capacity_sales__gt=0,
            translations__long_name=booking.route_name,
        ).exists():
            route["legs"] = [
                {
                    "stops": [
                        {
                            "location": {
                                "lat": "60.16783393799385",
                                "lon": "24.952470228154326",
                            },
                            "name": "Kauppatori, Lyypekinlaituri",
                            "stop_time": format_timestamp(departed_at),
                        },
                        {
                            "location": {
                                "lat": "60.16783393799385",
                                "lon": "24.952470228154326",
                            },
                            "name": "Korkeasaari",
                            "stop_time": format_timestamp(
                                departed_at + datetime.timedelta(hours=1)
                            ),
                        },
                    ]
                },
                {
                    "stops": [
                        {
                            "location": {
                                "lat": "60.16783393799385",
                                "lon": "24.952470228154326",
                            },
                            "name": "Korkeasaari",
                            "stop_time": format_timestamp(
                                departed_at + datetime.timedelta(hours=5)
                            ),
                        },
                        {
                            "location": {
                                "lat": "60.16783393799385",
                                "lon": "24.952470228154326",
                            },
                            "name": "Kauppatori, Lyypekinlaituri",
                            "stop_time": format_timestamp(
                                departed_at + datetime.timedelta(hours=6)
                            ),
                        },
                    ]
                },
            ]
    except Booking.DoesNotExist:
        pass

    return {
        "id": pk,
        "status": "CONFIRMED",
        "tickets": [
            {
                "agency": {
                    "logo": agency_image,
                    "name": "Ferry Lines",
                    "url": "https://www.ferry-lines.fi",
                },
                "created_at": format_timestamp(valid_from),
                "customer_type": {
                    "name": "Adult",
                    "description": "Adult ticket is the full price ticket",
                },
                "html": "<div>This is the ticket</div>",
                "id": "55619d53-bcc0-46df-aa7c-4840cb891262",
                "locale": "en",
                "maas_operator_id": "6046d689-06ce-4662-a193-d22cd754a1c2",
                "price": {
                    "amount_excluding_vat": "8.5",
                    "amount_total": "10",
                    "currency": "EUR",
                    "vat_amount": "1.5",
                    "vat_percentage": "15%",
                },
                "qr_code": ticket,
                "receipt_number": "1A2B3C4D5E6F7G8H",
                "refresh_at": format_timestamp(valid_to),
                "route": route,
                "schema_version": 2,
                "status": "CONFIRMED",
                "terms_url": "http://www.terms.and.conditions.fi",
                "ticket_type": {
                    "description": "Return ticket to Suomenlinna. Can be used as an open ticket on other departures.",
                    "instructions": "Be ready to show the ticket for the inspector.",
                    "name": "Return Ticket",
                },
                "validity": {
                    "activates_at": format_timestamp(valid_from),
                    "deactivates_at": format_timestamp(valid_to),
                    "ends_at": format_timestamp(valid_to),
                    "starts_at": format_timestamp(valid_from),
                },
            }
        ],
    }


def get_error_data(error_code):
    errors = {
        "MAX_CAPACITY_EXCEEDED": {
            "code": "MAX_CAPACITY_EXCEEDED",
        },
        "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED": {
            "code": "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED",
            "message": "Maximum number of tickets requested exceeded.",
        },
        "BOOKING_EXPIRED": {
            "code": "BOOKING_EXPIRED",
            "message": "Booking expired.",
            "details": "Your booking has totally expired.",
        },
        "BOOKING_ALREADY_CONFIRMED": {
            "code": "BOOKING_ALREADY_CONFIRMED",
        },
        "TICKET_SYSTEM_ERROR": {"code": "TICKET_SYSTEM_ERROR"},
        "BOOKING_NOT_CONFIRMED": {
            "code": "BOOKING_NOT_CONFIRMED",
            "message": "Booking is not confirmed. Confirm the booking to get it's details.",
        },
    }
    if error := errors.get(error_code):
        return {"error": error}
    return None
