"""
Custom DRF exception handler that returns consistent error shapes.

All error responses follow:
{
    "errors": [{"field": "...", "message": "..."}],   # validation errors
    "detail": "..."                                    # non-field errors
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {"detail": "An unexpected server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Normalise validation errors into a flat list
    if isinstance(response.data, dict):
        errors = []
        for field, messages in response.data.items():
            if field == "detail":
                continue
            if isinstance(messages, list):
                for msg in messages:
                    errors.append({"field": field, "message": str(msg)})
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
