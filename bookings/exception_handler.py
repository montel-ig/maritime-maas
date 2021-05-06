import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as original_exception_handler

from bookings.ticketing_system import (
    TicketingSystemNotBehavingError,
    TicketingSystemRequestError,
)

logger = logging.getLogger(__name__)


def _get_error_response(exc):
    return Response(
        {"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def exception_handler(exc, context):
    if isinstance(exc, TicketingSystemRequestError):
        return _get_error_response(exc)
    elif isinstance(exc, TicketingSystemNotBehavingError):
        logger.error(exc)
        return _get_error_response(exc)
    else:
        return original_exception_handler(exc, context)
