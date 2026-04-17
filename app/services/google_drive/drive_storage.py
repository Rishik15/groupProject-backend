import io
import os
import uuid
from mimetypes import guess_extension

from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


def _get_drive_service():
    service_account_file = current_app.config["GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE"]
    scopes = current_app.config["GOOGLE_DRIVE_SCOPES"]

    if not service_account_file:
        raise ValueError("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE is not configured")

    if not os.path.exists(service_account_file):
        raise FileNotFoundError(
            f"service account file not found: {service_account_file}"
        )

    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes,
    )

    return build("drive", "v3", credentials=creds)


def _escape_drive_query_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _find_child_folder(service, parent_folder_id: str, folder_name: str):
    safe_folder_name = _escape_drive_query_value(folder_name)

    query = (
        "mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false "
        f"and name = '{safe_folder_name}' "
        f"and '{parent_folder_id}' in parents"
    )

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=10,
    ).execute()

    files = response.get("files", [])
    return files[0]["id"] if files else None


def _create_folder(service, parent_folder_id: str, folder_name: str):
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }

    created = service.files().create(
        body=metadata,
        fields="id, name",
    ).execute()

    return created["id"]


def _get_or_create_user_folder(service, user_id: int):
    parent_folder_id = current_app.config["GOOGLE_DRIVE_PARENT_FOLDER_ID"]
    prefix = current_app.config["GOOGLE_DRIVE_USER_FOLDER_PREFIX"]

    if not parent_folder_id:
        raise ValueError("GOOGLE_DRIVE_PARENT_FOLDER_ID is not configured")

    folder_name = f"{prefix}{user_id}"

    existing_folder_id = _find_child_folder(service, parent_folder_id, folder_name)
    if existing_folder_id:
        return existing_folder_id

    return _create_folder(service, parent_folder_id, folder_name)


def _make_public(service, file_id: str):
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()


def _build_public_url(file_id: str):
    return f"https://drive.google.com/uc?id={file_id}"


def _build_safe_filename(original_filename: str, mimetype: str | None):
    ext = ""
    if original_filename and "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[1].lower()
    elif mimetype:
        guessed = guess_extension(mimetype)
        ext = guessed if guessed else ""

    return f"{uuid.uuid4().hex}{ext}"


def upload_meal_image_for_user(user_id: int, uploaded_file):
    if uploaded_file is None:
        raise ValueError("uploaded_file is required")

    if not getattr(uploaded_file, "filename", None):
        raise ValueError("uploaded file must have a filename")

    service = _get_drive_service()
    user_folder_id = _get_or_create_user_folder(service, user_id)

    file_bytes = uploaded_file.read()
    if not file_bytes:
        raise ValueError("uploaded file is empty")

    uploaded_file.stream.seek(0)

    mimetype = uploaded_file.mimetype or "application/octet-stream"
    safe_name = _build_safe_filename(uploaded_file.filename, mimetype)

    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=mimetype,
        resumable=False,
    )

    metadata = {
        "name": safe_name,
        "parents": [user_folder_id],
    }

    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, webViewLink",
    ).execute()

    file_id = created["id"]

    _make_public(service, file_id)

    return {
        "file_id": file_id,
        "file_name": created["name"],
        "photo_url": _build_public_url(file_id),
        "folder_id": user_folder_id,
    }