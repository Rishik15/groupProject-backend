from datetime import datetime

from app.services import run_query


def _coerce_db_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    raise TypeError("unsupported datetime value returned from db")


def create_progress_photo(user_id: int, photo_url: str, caption: str | None = None, taken_at: str | None = None):
    taken_at_value = None
    if taken_at is not None and str(taken_at).strip() != "":
        taken_at_value = datetime.fromisoformat(taken_at).isoformat()

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


def get_progress_photos(user_id: int):
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
        if row["taken_at"] is not None:
            row["taken_at"] = _coerce_db_datetime(row["taken_at"]).isoformat()
        row["created_at"] = _coerce_db_datetime(row["created_at"]).isoformat()
        row["updated_at"] = _coerce_db_datetime(row["updated_at"]).isoformat()

    return rows