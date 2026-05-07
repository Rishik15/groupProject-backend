from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _coerce_db_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.fromisoformat(value.replace(" ", "T"))

    raise TypeError("unsupported datetime value returned from db")


def _local_input_to_utc_string(value, user_timezone: str | None):
    if value is None or str(value).strip() == "":
        return None

    cleaned_value = str(value).strip().replace("Z", "+00:00")
    parsed_datetime = datetime.fromisoformat(cleaned_value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(
            tzinfo=ZoneInfo(_get_valid_timezone(user_timezone))
        )

    utc_datetime = parsed_datetime.astimezone(timezone.utc)

    return utc_datetime.strftime("%Y-%m-%d %H:%M:%S")


def _format_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    parsed_datetime = _coerce_db_datetime(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    local_datetime = parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    )

    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def _serialize_progress_photo(row, user_timezone: str | None = None):
    if row is None:
        return None

    row["taken_at"] = _format_datetime(row.get("taken_at"), user_timezone)
    row["created_at"] = _format_datetime(row.get("created_at"), user_timezone)
    row["updated_at"] = _format_datetime(row.get("updated_at"), user_timezone)

    return row


def create_progress_photo(
    user_id: int,
    photo_url: str,
    caption: str | None = None,
    taken_at: str | None = None,
    user_timezone: str | None = None,
):
    taken_at_value = _local_input_to_utc_string(taken_at, user_timezone)

    run_query(
        """
        INSERT INTO progress_photo
        (
            user_id,
            photo_url,
            caption,
            taken_at
        )
        VALUES
        (
            :user_id,
            :photo_url,
            :caption,
            :taken_at
        )
        """,
        {
            "user_id": user_id,
            "photo_url": photo_url,
            "caption": caption,
            "taken_at": taken_at_value,
        },
        fetch=False,
        commit=True,
    )

    created = run_query(
        """
        SELECT LAST_INSERT_ID() AS progress_photo_id
        """,
        {},
        fetch=True,
        commit=False,
    )

    if not created or created[0]["progress_photo_id"] is None:
        raise Exception("failed to fetch created progress photo id")

    return created[0]["progress_photo_id"]


def get_progress_photos(user_id: int, user_timezone: str | None = None):
    rows = run_query(
        """
        SELECT
            progress_photo_id,
            user_id,
            photo_url,
            caption,
            taken_at,
            created_at,
            updated_at
        FROM progress_photo
        WHERE user_id = :user_id
        ORDER BY
            COALESCE(taken_at, created_at) DESC,
            progress_photo_id DESC
        """,
        {
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    for row in rows:
        _serialize_progress_photo(row, user_timezone)

    return rows


def get_progress_photo_by_id_for_user(
    user_id: int,
    progress_photo_id: int,
    user_timezone: str | None = None,
):
    rows = run_query(
        """
        SELECT
            progress_photo_id,
            user_id,
            photo_url,
            caption,
            taken_at,
            created_at,
            updated_at
        FROM progress_photo
        WHERE user_id = :user_id
          AND progress_photo_id = :progress_photo_id
        LIMIT 1
        """,
        {
            "user_id": user_id,
            "progress_photo_id": progress_photo_id,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    return _serialize_progress_photo(rows[0], user_timezone)


def delete_progress_photo(user_id: int, progress_photo_id: int):
    run_query(
        """
        DELETE FROM progress_photo
        WHERE user_id = :user_id
          AND progress_photo_id = :progress_photo_id
        """,
        {
            "user_id": user_id,
            "progress_photo_id": progress_photo_id,
        },
        fetch=False,
        commit=True,
    )

    return True
