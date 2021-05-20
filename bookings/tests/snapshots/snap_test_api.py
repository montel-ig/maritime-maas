# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_confirm_booking[False] 1"] = [
    {
        "agency": {"logo_url": "http://www.agency.com/logo.png", "name": "MaaS Line"},
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
        "qr_code": "QR_CODE",
        "refresh_at": "2021-04-21T00:00:00Z",
        "terms_of_use": "http://www.terms.and.conditions.fi",
        "ticket_html": "<div>...</div>",
        "ticket_type": "Päivälippu",
        "valid_from": "2021-04-20T00:00:00Z",
        "valid_to": "2021-04-21T00:00:00Z",
    }
]

snapshots["test_confirm_booking[True] 1"] = [
    {
        "agency": {"logo_url": "http://www.agency.com/logo.png", "name": "MaaS Line"},
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
        "qr_code": "QR_CODE",
        "refresh_at": "2021-04-21T00:00:00Z",
        "terms_of_use": "http://www.terms.and.conditions.fi",
        "ticket_html": "<div>...</div>",
        "ticket_type": "Päivälippu",
        "valid_from": "2021-04-20T00:00:00Z",
        "valid_to": "2021-04-21T00:00:00Z",
    }
]

snapshots["test_create_booking_illegal_departures[False-departure_indices2] 1"] = {
    "departure_ids": ["All departures must belong to the same route."]
}

snapshots["test_create_booking_illegal_departures[True-departure_indices0] 1"] = {
    "departure_ids": ["All departures must belong to the same route."]
}

snapshots["test_create_booking_illegal_departures[True-departure_indices1] 1"] = {
    "departure_ids": ["All departures must belong to the same route."]
}

snapshots["test_create_booking_illegal_rider_category_or_fare[0-1] 1"] = {
    "tickets": [
        {
            "ticket_type_id": [
                'Invalid ID "00000000-0000-0000-0000-000000000001" - object does not exist.'
            ]
        }
    ]
}

snapshots["test_create_booking_illegal_rider_category_or_fare[1-0] 1"] = {
    "tickets": [
        {
            "customer_type_id": [
                'Invalid ID "00000000-0000-0000-0000-000000000003" - object does not exist.'
            ]
        }
    ]
}

snapshots["test_create_booking_illegal_rider_category_or_fare[1-1] 1"] = {
    "tickets": [
        {
            "ticket_type_id": [
                'Invalid ID "00000000-0000-0000-0000-000000000001" - object does not exist.'
            ]
        }
    ]
}

snapshots["test_create_booking_no_permission 1"] = {
    "departure_ids": [
        'Invalid ID "00000000-0000-0000-0000-000000000004" - object does not exist.'
    ]
}

snapshots["test_ticketing_system_errors[None-200-confirmation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-200-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-400-confirmation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response0-422-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response0-422-reservation] 1"] = {
    "error": {"code": "MAX_CAPACITY_EXCEEDED", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response1-400-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response1-400-reservation] 1"] = {
    "error": {
        "code": "MAX_NUMBER_OF_TICKETS_REQUESTED_EXCEEDED",
        "details": "",
        "message": "Maximum number of tickets requested exceeded.",
    }
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response10-201-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response10-201-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response11-201-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response11-201-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response12-201-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response12-201-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response13-422-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response13-422-reservation] 1"
] = {"error": {"code": "MAX_CAPACITY_EXCEEDED", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response14-422-confirmation] 1"
] = {"error": {"code": "BOOKING_ALREADY_CONFIRMED", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response14-422-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response2-400-confirmation] 1"
] = {
    "error": {
        "code": "BOOKING_EXPIRED",
        "details": "Your booking has been totally expired.",
        "message": "Booking expired.",
    }
}

snapshots["test_ticketing_system_errors[ticketing_api_response2-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response3-422-confirmation] 1"
] = {"error": {"code": "BOOKING_ALREADY_CONFIRMED", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response3-422-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response4-400-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response4-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response5-400-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response5-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response6-500-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response6-500-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response9-200-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response9-200-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}
