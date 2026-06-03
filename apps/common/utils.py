"""
Shared utility helpers.
"""
import uuid
import os


def upload_to(subfolder: str):
    """
    Returns an upload_to callable for ImageField / FileField.
    Files are stored as: media/<subfolder>/<uuid>.<ext>
    """
    def handler(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        new_name = f"{uuid.uuid4().hex}{ext}"
        return os.path.join(subfolder, new_name)
    return handler


def build_absolute_uri(request, path: str) -> str:
    """Build a full absolute URI from a relative path."""
    return request.build_absolute_uri(path)
