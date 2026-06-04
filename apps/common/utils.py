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


def upload_file_to_s3_or_local(request, file_obj, subfolder='uploads'):
    """
    Uploads a file to Cloudinary if credentials (either CLOUDINARY_URL or keys)
    are provided in the environment.
    Otherwise, falls back to Django's local media storage.
    Returns the absolute URL of the uploaded file.
    """
    import cloudinary
    import cloudinary.uploader
    from django.conf import settings
    from django.core.files.storage import FileSystemStorage

    cloudinary_url = os.environ.get('CLOUDINARY_URL')
    cloudinary_cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    cloudinary_api_key = os.environ.get('CLOUDINARY_API_KEY')
    cloudinary_api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if cloudinary_url or (cloudinary_cloud_name and cloudinary_api_key and cloudinary_api_secret):
        try:
            # Configure Cloudinary
            if cloudinary_url:
                # If CLOUDINARY_URL is present, SDK will automatically read it.
                # Just in case, we can set it explicitly or config secure=True
                cloudinary.config(secure=True)
            else:
                cloudinary.config(
                    cloud_name=cloudinary_cloud_name,
                    api_key=cloudinary_api_key,
                    api_secret=cloudinary_api_secret,
                    secure=True
                )
            # Upload the file directly to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file_obj,
                folder=subfolder
            )
            secure_url = upload_result.get("secure_url")
            if secure_url:
                return secure_url
        except Exception as e:
            print(f"Cloudinary upload failed: {e}. Falling back to local storage.")

    # Fallback to local storage
    ext = os.path.splitext(file_obj.name)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    fs = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, subfolder),
        base_url=f"{settings.MEDIA_URL}{subfolder}/"
    )
    saved_filename = fs.save(unique_filename, file_obj)
    local_relative_url = fs.url(saved_filename)
    return build_absolute_uri(request, local_relative_url)



