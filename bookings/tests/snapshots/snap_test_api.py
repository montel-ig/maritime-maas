# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_confirm_booking[False] 1"] = [
    {
        "agency": {
            "logo": "AGENCY_IMAGE",
            "name": "Ferry Lines",
            "url": "https://www.ferry-lines.fi",
        },
        "created_at": "2021-04-20T00:00:00Z",
        "customer_type": {
            "description": "Adult ticket is the full price ticket",
            "name": "Adult",
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
        "qr_code": "QR_CODE",
        "receipt_number": "1A2B3C4D5E6F7G8H",
        "refresh_at": "2021-04-21T00:00:00Z",
        "route": {
            "description": "Nice scenic route from Kauppatori to Korkeasaari",
            "name": "Kauppatori - Korkeasaari",
        },
        "schema_version": 2,
        "status": "CONFIRMED",
        "terms_url": "http://www.terms.and.conditions.fi",
        "ticket_type": {
            "description": "Return ticket to Suomenlinna. Can be used as an open ticket on other departures.",
            "instructions": "Be ready to show the ticket for the inspector.",
            "name": "Return Ticket",
        },
        "validity": {
            "activates_at": "2021-04-20T00:00:00Z",
            "deactivates_at": "2021-04-21T00:00:00Z",
            "ends_at": "2021-04-21T00:00:00Z",
            "starts_at": "2021-04-20T00:00:00Z",
        },
    }
]

snapshots["test_confirm_booking[True] 1"] = [
    {
        "agency": {
            "logo": "AGENCY_IMAGE",
            "name": "Ferry Lines",
            "url": "https://www.ferry-lines.fi",
        },
        "created_at": "2021-04-20T00:00:00Z",
        "customer_type": {
            "description": "Adult ticket is the full price ticket",
            "name": "Adult",
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
        "qr_code": "QR_CODE",
        "receipt_number": "1A2B3C4D5E6F7G8H",
        "refresh_at": "2021-04-21T00:00:00Z",
        "route": {
            "description": "Nice scenic route from Kauppatori to Korkeasaari",
            "name": "Kauppatori - Korkeasaari",
        },
        "schema_version": 2,
        "status": "CONFIRMED",
        "terms_url": "http://www.terms.and.conditions.fi",
        "ticket_type": {
            "description": "Return ticket to Suomenlinna. Can be used as an open ticket on other departures.",
            "instructions": "Be ready to show the ticket for the inspector.",
            "name": "Return Ticket",
        },
        "validity": {
            "activates_at": "2021-04-20T00:00:00Z",
            "deactivates_at": "2021-04-21T00:00:00Z",
            "ends_at": "2021-04-21T00:00:00Z",
            "starts_at": "2021-04-20T00:00:00Z",
        },
    }
]

snapshots[
    "test_create_booking_capacity_sales_required_for_outbound_and_inbound[3-direction_ids2-False] 1"
] = {
    "departure_ids": ["Exactly one outbound departure must be selected for this route."]
}

snapshots[
    "test_create_booking_capacity_sales_required_for_outbound_and_inbound[3-direction_ids4-False] 1"
] = {
    "departure_ids": ["Exactly one outbound departure must be selected for this route."]
}

snapshots[
    "test_create_booking_capacity_sales_required_for_outbound_and_inbound[3-direction_ids5-False] 1"
] = {
    "departure_ids": ["Exactly one outbound departure must be selected for this route."]
}

snapshots[
    "test_create_booking_capacity_sales_required_for_outbound_and_inbound[4-direction_ids3-False] 1"
] = {
    "departure_ids": ["Exactly one inbound departure must be selected for this route."]
}

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

snapshots["test_fetch_availability request 1 body"] = {
    "departures": [
        {"date": "2021-04-28", "trip_id": "source_id of trip 1"},
        {"date": "2021-04-28", "trip_id": "source_id of trip 2"},
    ]
}

snapshots["test_fetch_availability request 1 url"] = "http://example.com/allowed1/"

snapshots["test_fetch_availability request 2 body"] = {
    "departures": [
        {"date": "2021-04-29", "trip_id": "source_id of trip 3"},
        {"date": "2021-04-29", "trip_id": "source_id of trip 4"},
    ]
}

snapshots["test_fetch_availability request 2 url"] = "http://example.com/allowed2/"

snapshots["test_fetch_availability response"] = [
    {
        "available": 1,
        "departure_id": "00000000-0000-0000-0000-000000000000",
        "total": 10,
    },
    {
        "available": 5,
        "departure_id": "00000000-0000-0000-0000-000000000001",
        "total": None,
    },
    {
        "available": 0,
        "departure_id": "00000000-0000-0000-0000-000000000003",
        "total": 100,
    },
]

snapshots["test_retrieve_confirmed_booking 1"] = [
    {
        "agency": {
            "logo": "AGENCY_IMAGE",
            "name": "Ferry Lines",
            "url": "https://www.ferry-lines.fi",
        },
        "created_at": "2021-04-20T00:00:00Z",
        "customer_type": {
            "description": "Adult ticket is the full price ticket",
            "name": "Adult",
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
        "qr_code": "QR_CODE",
        "receipt_number": "1A2B3C4D5E6F7G8H",
        "refresh_at": "2021-04-21T00:00:00Z",
        "route": {
            "description": "Nice scenic route from Kauppatori to Korkeasaari",
            "name": "Kauppatori - Korkeasaari",
        },
        "schema_version": 2,
        "status": "CONFIRMED",
        "terms_url": "http://www.terms.and.conditions.fi",
        "ticket_type": {
            "description": "Return ticket to Suomenlinna. Can be used as an open ticket on other departures.",
            "instructions": "Be ready to show the ticket for the inspector.",
            "name": "Return Ticket",
        },
        "validity": {
            "activates_at": "2021-04-20T00:00:00Z",
            "deactivates_at": "2021-04-21T00:00:00Z",
            "ends_at": "2021-04-21T00:00:00Z",
            "starts_at": "2021-04-20T00:00:00Z",
        },
    }
]

snapshots["test_ticketing_system_errors[None-200-confirmation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-200-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-200-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-400-confirmation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[None-400-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response0-422-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response0-422-reservation] 1"] = {
    "error": {"code": "MAX_CAPACITY_EXCEEDED", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[ticketing_api_response0-422-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
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

snapshots["test_ticketing_system_errors[ticketing_api_response1-400-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response10-201-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response10-201-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response10-201-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response11-201-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response11-201-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response11-201-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response12-201-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response12-201-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response12-201-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response13-422-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response13-422-reservation] 1"
] = {"error": {"code": "MAX_CAPACITY_EXCEEDED", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response13-422-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response14-422-confirmation] 1"
] = {"error": {"code": "BOOKING_ALREADY_CONFIRMED", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response14-422-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response14-422-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response15-422-confirmation] 1"
] = {"error": {"code": "TICKET_SALES_ENDED", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response15-422-reservation] 1"
] = {"error": {"code": "TICKET_SALES_ENDED", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response15-422-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response16-422-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response16-422-reservation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response16-422-retrieve] 1"] = {
    "error": {
        "code": "BOOKING_NOT_CONFIRMED",
        "details": "",
        "message": "Booking is not confirmed. Confirm the booking to get it's details.",
    }
}

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

snapshots["test_ticketing_system_errors[ticketing_api_response2-400-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response3-422-confirmation] 1"
] = {"error": {"code": "BOOKING_ALREADY_CONFIRMED", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response3-422-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[ticketing_api_response3-422-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response4-400-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response4-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[ticketing_api_response4-400-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response5-400-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response5-400-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[ticketing_api_response5-400-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response6-500-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response6-500-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[ticketing_api_response6-500-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots[
    "test_ticketing_system_errors[ticketing_api_response9-200-confirmation] 1"
] = {"error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}}

snapshots["test_ticketing_system_errors[ticketing_api_response9-200-reservation] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}

snapshots["test_ticketing_system_errors[ticketing_api_response9-200-retrieve] 1"] = {
    "error": {"code": "TICKET_SYSTEM_ERROR", "details": "", "message": ""}
}
