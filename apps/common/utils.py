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
    Uploads a file to MinIO/S3 if credentials are provided in the environment.
    Otherwise, falls back to Django's local media storage.
    Returns the absolute URL of the uploaded file.
    """
    import boto3
    from botocore.client import Config
    from django.conf import settings
    from django.core.files.storage import FileSystemStorage

    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    endpoint_url = os.environ.get('AWS_S3_ENDPOINT_URL')  # e.g., http://localhost:9000 for MinIO
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

    ext = os.path.splitext(file_obj.name)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    key_path = f"{subfolder}/{unique_filename}"

    if aws_access_key and aws_secret_key and bucket_name:
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                endpoint_url=endpoint_url,
                region_name=region_name,
                config=Config(signature_version='s3v4')
            )
            # Upload the file
            s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                key_path,
                ExtraArgs={
                    'ContentType': getattr(file_obj, 'content_type', 'image/jpeg'),
                }
            )
            # Return URL
            if endpoint_url:
                endpoint_clean = endpoint_url.rstrip('/')
                return f"{endpoint_clean}/{bucket_name}/{key_path}"
            else:
                return f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{key_path}"
        except Exception as e:
            print(f"S3/MinIO upload failed: {e}. Falling back to local storage.")

    # Fallback to local storage
    fs = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, subfolder),
        base_url=f"{settings.MEDIA_URL}{subfolder}/"
    )
    saved_filename = fs.save(unique_filename, file_obj)
    local_relative_url = fs.url(saved_filename)
    return build_absolute_uri(request, local_relative_url)

