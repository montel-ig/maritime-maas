import base64
import datetime
import uuid
from pathlib import PurePath

from django.utils import timezone


def format_timestamp(d: datetime.datetime):
    return f"{d.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"


def get_reservation_data() -> dict:
    return {"id": str(uuid.uuid4()), "status": "RESERVED"}


def get_confirmations_data(pk) -> dict:
    path = PurePath(__file__).parent.joinpath("data", "ticket_qr.png")
    with open(path.as_posix(), "rb") as f:
        ticket = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
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
