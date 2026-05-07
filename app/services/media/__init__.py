import uuid
from mimetypes import guess_extension

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}

ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}


def _get_extension(uploaded_file):
    original_filename = getattr(uploaded_file, "filename", "") or ""
    safe_name = secure_filename(original_filename)

    if "." in safe_name:
        ext = "." + safe_name.rsplit(".", 1)[1].lower()
        if ext:
            return ext

    mimetype = getattr(uploaded_file, "mimetype", None)
    guessed = guess_extension(mimetype) if mimetype else None
    return guessed or ""


def _validate_category(category: str):
    if not category:
        raise ValueError("category is required")

    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    )

    if any(ch not in allowed_chars for ch in category):
        raise ValueError("category contains invalid characters")


def _configure_cloudinary():
    import cloudinary

    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def _upload_to_cloudinary(
    uploaded_file, folder: str, resource_type: str, public_id: str
):
    import cloudinary.uploader

    _configure_cloudinary()

    result = cloudinary.uploader.upload(
        uploaded_file,
        folder=folder,
        public_id=public_id,
        resource_type=resource_type,
        overwrite=False,
    )

    secure_url = result.get("secure_url")
    cloudinary_public_id = result.get("public_id")

    if not secure_url or not cloudinary_public_id:
        raise RuntimeError("Cloudinary upload failed")

    return {
        "url": secure_url,
        "public_id": cloudinary_public_id,
        "resource_type": result.get("resource_type"),
        "format": result.get("format"),
        "bytes": result.get("bytes"),
    }


def save_user_uploaded_image(user_id: int, uploaded_file, category: str):
    if user_id is None:
        raise ValueError("user_id is required")

    if uploaded_file is None:
        raise ValueError("uploaded_file is required")

    if not getattr(uploaded_file, "filename", None):
        raise ValueError("uploaded file must have a filename")

    _validate_category(category)

    mimetype = getattr(uploaded_file, "mimetype", None)

    if mimetype not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError("uploaded file must be a supported image type")

    file_bytes = uploaded_file.read()

    if not file_bytes:
        raise ValueError("uploaded file is empty")

    uploaded_file.stream.seek(0)

    ext = _get_extension(uploaded_file)
    filename = f"{uuid.uuid4().hex}{ext}"
    public_id_without_ext = filename.rsplit(".", 1)[0]

    folder = f"{category}/user_{int(user_id)}"

    result = _upload_to_cloudinary(
        uploaded_file=uploaded_file,
        folder=folder,
        resource_type="image",
        public_id=public_id_without_ext,
    )

    return {
        "photo_url": result["url"],
        "file_name": filename,
        "category": category,
        "relative_url": result["public_id"],
        "absolute_path": None,
        "storage_backend": "cloudinary",
        "cloudinary_public_id": result["public_id"],
    }


def save_meal_image_for_user(user_id: int, uploaded_file):
    meal_category = current_app.config.get("MEAL_IMAGES_SUBDIR", "meal_images")

    return save_user_uploaded_image(
        user_id=user_id,
        uploaded_file=uploaded_file,
        category=meal_category,
    )


def save_exercise_video(coach_id: int, uploaded_file):
    if coach_id is None:
        raise ValueError("coach_id is required")

    if uploaded_file is None:
        raise ValueError("uploaded_file is required")

    if not getattr(uploaded_file, "filename", None):
        raise ValueError("uploaded file must have a filename")

    mimetype = getattr(uploaded_file, "mimetype", None)

    if mimetype not in ALLOWED_VIDEO_MIME_TYPES:
        raise ValueError("uploaded file must be a supported video type")

    file_bytes = uploaded_file.read()

    if not file_bytes:
        raise ValueError("uploaded file is empty")

    uploaded_file.stream.seek(0)

    ext = _get_extension(uploaded_file)
    filename = f"{uuid.uuid4().hex}{ext}"
    public_id_without_ext = filename.rsplit(".", 1)[0]

    folder = f"exercise_videos/coach_{int(coach_id)}"

    result = _upload_to_cloudinary(
        uploaded_file=uploaded_file,
        folder=folder,
        resource_type="video",
        public_id=public_id_without_ext,
    )

    return {
        "video_url": result["url"],
        "file_name": filename,
        "relative_url": result["public_id"],
        "absolute_path": None,
        "storage_backend": "cloudinary",
        "cloudinary_public_id": result["public_id"],
    }
