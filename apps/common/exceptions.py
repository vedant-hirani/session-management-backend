"""
Custom DRF exception handler that returns consistent error shapes.

All error responses follow:
{
    "errors": [{"field": "...", "message": "..."}],   # validation errors
    "detail": "..."                                    # non-field errors
}
"""
import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, DatabaseError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Handle Django-specific validation errors and convert them to DRF's ValidationErrors
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            exc = DRFValidationError(detail=exc.message_dict)
        elif hasattr(exc, "messages"):
            exc = DRFValidationError(detail=exc.messages)
        else:
            exc = DRFValidationError(detail=str(exc))

    # Handle database integrity issues (e.g. duplicate keys)
    if isinstance(exc, IntegrityError):
        logger.error("Database integrity error: %s", str(exc), exc_info=True)
        # Check for common unique constraint messages
        error_msg = str(exc)
        detail = "A database integrity constraint was violated."
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            detail = "This record or unique identifier already exists."
        
        return Response(
            {
                "detail": detail,
                "errors": [{"field": "database", "message": error_msg}]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Let DRF handle standard API exceptions first
    response = exception_handler(exc, context)

    # If DRF doesn't handle the exception, handle it as a 500 server error
    if response is None:
        logger.error("Unhandled exception: %s", str(exc), exc_info=True)
        # Catch other database operational errors
        if isinstance(exc, DatabaseError):
            return Response(
                {
                    "detail": "A database error occurred.",
                    "errors": [{"field": "database", "message": str(exc)}]
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(
            {
                "detail": "An unexpected server error occurred.",
                "errors": [{"field": "server", "message": str(exc)}]
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Normalise DRF validation errors into a flat list
    if isinstance(response.data, dict):
        errors = []
        for field, messages in response.data.items():
            if field == "detail":
                continue
            if isinstance(messages, list):
                for msg in messages:
                    errors.append({"field": field, "message": str(msg)})
            elif isinstance(messages, dict):
                for subfield, submsg in messages.items():
                    errors.append({"field": f"{field}.{subfield}", "message": str(submsg)})
            else:
                errors.append({"field": field, "message": str(messages)})

        detail = response.data.get("detail", None)
        new_data = {}
        if detail:
            new_data["detail"] = str(detail)
        if errors:
            new_data["errors"] = errors
        if not new_data:
            new_data = response.data

        response.data = new_data

    return response
