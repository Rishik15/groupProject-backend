import os
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

    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    if any(ch not in allowed_chars for ch in category):
        raise ValueError("category contains invalid characters")


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

    media_root = current_app.config["MEDIA_ROOT"]
    user_dir = os.path.join(media_root, category, f"user_{int(user_id)}")
    os.makedirs(user_dir, exist_ok=True)

    abs_path = os.path.join(user_dir, filename)

    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    url_prefix = current_app.config["MEDIA_URL_PREFIX"].rstrip("/")
    relative_url = f"{category}/user_{int(user_id)}/{filename}"
    photo_url = f"{url_prefix}/{relative_url}"

    return {
        "photo_url": photo_url,
        "file_name": filename,
        "category": category,
        "relative_url": relative_url,
        "absolute_path": abs_path,
    }


def save_meal_image_for_user(user_id: int, uploaded_file):
    meal_category = current_app.config.get("MEAL_IMAGES_SUBDIR", "meal_images")
    return save_user_uploaded_image(
        user_id=user_id,
        uploaded_file=uploaded_file,
        category=meal_category,
    )


ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}

def save_exercise_video(coach_id: int, uploaded_file):
    if coach_id is None:
        raise ValueError("coach_id is required")

    if uploaded_file is None:
        raise ValueError("uploaded_file is required")

    mimetype = getattr(uploaded_file, "mimetype", None)
    if mimetype not in ALLOWED_VIDEO_MIME_TYPES:
        raise ValueError("uploaded file must be a supported video type (mp4, webm, mov)")

    file_bytes = uploaded_file.read()
    if not file_bytes:
        raise ValueError("uploaded file is empty")

    uploaded_file.stream.seek(0)

    ext = _get_extension(uploaded_file)
    filename = f"{uuid.uuid4().hex}{ext}"

    media_root = current_app.config["MEDIA_ROOT"]
    video_dir = os.path.join(media_root, "exercise_videos", f"coach_{int(coach_id)}")
    os.makedirs(video_dir, exist_ok=True)

    abs_path = os.path.join(video_dir, filename)
    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    url_prefix = current_app.config["MEDIA_URL_PREFIX"].rstrip("/")
    relative_url = f"exercise_videos/coach_{int(coach_id)}/{filename}"
    video_url = f"{url_prefix}/{relative_url}"

    return {
        "video_url": video_url,
        "file_name": filename,
        "relative_url": relative_url,
        "absolute_path": abs_path,
    }