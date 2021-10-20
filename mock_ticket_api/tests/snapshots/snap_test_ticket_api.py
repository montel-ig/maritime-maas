# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_ticket_confirmation 1"] = {
    "id": "71ck37_1d",
    "status": "CONFIRMED",
    "tickets": [
        {
            "agency": {
                "logo_url": "http://www.agency.com/logo.png",
                "name": "MaaS Line",
            },
            "amount": 12,
            "currency": "EUR",
            "customer_type": "Aikuinen",
            "departures": [
                {
                    "depart_at": "2021-04-20T01:00:00Z",
                    "from": "Kauppatori",
                    "to": "Vallisaari",
                }
            ],
            "description": "This is the description of the ticket",
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "instructions": "These are the instructions of the ticket",
            "locale": "fi",
            "name": "Day in Vallisaari",
            "qr_code": "data:image/png;base64,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",  # noqa: E501
            "refresh_at": "2021-04-21T00:00:00Z",
            "terms_of_use": "http://www.terms.and.conditions.fi",
            "ticket_html": "<div>...</div>",
            "ticket_type": "Päivälippu",
            "valid_from": "2021-04-20T00:00:00Z",
            "valid_to": "2021-04-21T00:00:00Z",
        }
    ],
}

snapshots["test_ticket_details 1"] = {
    "id": "71ck37_1d",
    "status": "CONFIRMED",
    "tickets": [
        {
            "agency": {
                "logo_url": "http://www.agency.com/logo.png",
                "name": "MaaS Line",
            },
            "amount": 12,
            "currency": "EUR",
            "customer_type": "Aikuinen",
            "departures": [
                {
                    "depart_at": "2021-04-20T01:00:00Z",
                    "from": "Kauppatori",
                    "to": "Vallisaari",
                }
            ],
            "description": "This is the description of the ticket",
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "instructions": "These are the instructions of the ticket",
            "locale": "fi",
            "name": "Day in Vallisaari",
            "qr_code": "data:image/png;base64,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",  # noqa: E501
            "refresh_at": "2021-04-21T00:00:00Z",
            "terms_of_use": "http://www.terms.and.conditions.fi",
            "ticket_html": "<div>...</div>",
            "ticket_type": "Päivälippu",
            "valid_from": "2021-04-20T00:00:00Z",
            "valid_to": "2021-04-21T00:00:00Z",
        }
    ],
}

snapshots["test_ticket_reservation 1"] = {
    "id": "00000000-0000-0000-0000-000000000001",
    "status": "RESERVED",
}
