import io
import os
import uuid
from mimetypes import guess_extension

from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from .oauth_storage import (
    get_effective_google_drive_connection,
    save_google_drive_connection,
)


def build_google_auth_flow(state: str | None = None):
    client_secrets_file = current_app.config["GOOGLE_OAUTH_CLIENT_SECRETS_FILE"]
    redirect_uri = current_app.config["GOOGLE_OAUTH_REDIRECT_URI"]
    scopes = current_app.config["GOOGLE_OAUTH_SCOPES"]

    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(
            f"oauth client secrets file not found: {client_secrets_file}"
        )

    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow


def _get_credentials_for_user(user_id: int):
    connection = get_effective_google_drive_connection(user_id)
    if connection is None:
        raise ValueError("No Google Drive connection is configured for uploads")

    creds = Credentials(
        token=connection["access_token"],
        refresh_token=connection["refresh_token"],
        token_uri=connection["token_uri"],
        client_id=connection["client_id"],
        scopes=connection["scopes"],
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        save_google_drive_connection(
            account_scope=connection["account_scope"],
            owner_user_id=connection.get("owner_user_id"),
            connected_by_user_id=connection["connected_by_user_id"],
            google_email=connection["google_email"],
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            scopes=list(creds.scopes or connection["scopes"]),
            root_folder_id=connection.get("root_folder_id"),
        )

    return creds, connection


def _get_drive_service_for_user(user_id: int):
    creds, connection = _get_credentials_for_user(user_id)
    service = build("drive", "v3", credentials=creds)
    return service, connection


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


def _find_root_folder(service, connection):
    existing_root_folder_id = connection.get("root_folder_id")
    if existing_root_folder_id:
        return existing_root_folder_id

    root_folder_name = current_app.config["GOOGLE_DRIVE_ROOT_FOLDER_NAME"]
    safe_root_name = _escape_drive_query_value(root_folder_name)

    query = (
        "mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false "
        f"and name = '{safe_root_name}' "
        "and 'root' in parents"
    )

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=10,
    ).execute()

    files = response.get("files", [])
    if files:
        root_folder_id = files[0]["id"]
    else:
        created = service.files().create(
            body={
                "name": root_folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": ["root"],
            },
            fields="id, name",
        ).execute()
        root_folder_id = created["id"]

    save_google_drive_connection(
        account_scope=connection["account_scope"],
        owner_user_id=connection.get("owner_user_id"),
        connected_by_user_id=connection["connected_by_user_id"],
        google_email=connection["google_email"],
        access_token=connection["access_token"],
        refresh_token=connection["refresh_token"],
        token_uri=connection["token_uri"],
        client_id=connection["client_id"],
        scopes=connection["scopes"],
        root_folder_id=root_folder_id,
    )

    return root_folder_id


def _create_folder(service, parent_folder_id: str, folder_name: str):
    created = service.files().create(
        body={
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        },
        fields="id, name",
    ).execute()

    return created["id"]


def _get_or_create_user_folder(service, user_id: int, connection):
    root_folder_id = _find_root_folder(service, connection)
    prefix = current_app.config["GOOGLE_DRIVE_USER_FOLDER_PREFIX"]
    folder_name = f"{prefix}{user_id}"

    existing_folder_id = _find_child_folder(service, root_folder_id, folder_name)
    if existing_folder_id:
        return existing_folder_id

    return _create_folder(service, root_folder_id, folder_name)


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

    service, connection = _get_drive_service_for_user(user_id)
    user_folder_id = _get_or_create_user_folder(service, user_id, connection)

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

    created = service.files().create(
        body={
            "name": safe_name,
            "parents": [user_folder_id],
        },
        media_body=media,
        fields="id, name",
    ).execute()

    file_id = created["id"]

    _make_public(service, file_id)

    return {
        "file_id": file_id,
        "file_name": created["name"],
        "photo_url": _build_public_url(file_id),
        "folder_id": user_folder_id,
        "credential_source": connection["account_scope"],
    }