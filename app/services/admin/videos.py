from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _format_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        try:
            parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))
        except (ValueError, TypeError):
            return str(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    local_datetime = parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    )

    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def _shape_video_row(row, user_timezone: str | None = None):
    return {
        "exercise_id": row["exercise_id"],
        "exercise_name": row.get("exercise_name"),
        "equipment": row.get("equipment"),
        "video_url": row["video_url"],
        "video_status": row["video_status"],
        "video_review_note": row["video_review_note"],
        "video_reviewed_by": row["video_reviewed_by"],
        "created_by": row.get("created_by"),
        "created_at": _format_datetime(row["created_at"], user_timezone),
        "updated_at": _format_datetime(row["updated_at"], user_timezone),
    }


def _get_video_target_row(exercise_id: int):
    rows = run_query(
        """
        SELECT
            exercise_id,
            exercise_name,
            equipment,
            video_url,
            video_status,
            video_review_note,
            video_reviewed_by,
            created_by,
            created_at,
            updated_at
        FROM exercise
        WHERE exercise_id = :exercise_id
        """,
        params={"exercise_id": int(exercise_id)},
        fetch=True,
        commit=False,
    )

    if not rows:
        raise ValueError("Exercise not found")

    return rows[0]


def get_pending_admin_videos(user_id: int, user_timezone: str | None = None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            exercise_id,
            exercise_name,
            equipment,
            video_url,
            video_status,
            video_review_note,
            video_reviewed_by,
            created_by,
            created_at,
            updated_at
        FROM exercise
        WHERE video_url IS NOT NULL
          AND video_status = 'pending'
        ORDER BY updated_at DESC, exercise_id DESC
        """,
        fetch=True,
        commit=False,
    )

    return [_shape_video_row(row, user_timezone) for row in rows]


def approve_admin_video(user_id: int, exercise_id, user_timezone: str | None = None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not exercise_id:
        raise ValueError("exercise_id is required")

    existing = _get_video_target_row(int(exercise_id))

    if not existing["video_url"]:
        raise ValueError("Exercise has no video to approve")

    run_query(
        """
        UPDATE exercise
        SET
            video_status = 'approved',
            video_review_note = NULL,
            video_reviewed_by = :admin_id
        WHERE exercise_id = :exercise_id
        """,
        params={
            "admin_id": user_id,
            "exercise_id": int(exercise_id),
        },
        fetch=False,
        commit=True,
    )

    updated = _get_video_target_row(int(exercise_id))
    return _shape_video_row(updated, user_timezone)


def reject_admin_video(
    user_id: int,
    exercise_id,
    video_review_note=None,
    user_timezone: str | None = None,
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not exercise_id:
        raise ValueError("exercise_id is required")

    existing = _get_video_target_row(int(exercise_id))

    if not existing["video_url"]:
        raise ValueError("Exercise has no video to reject")

    final_note = video_review_note if video_review_note else "Rejected by admin"

    run_query(
        """
        UPDATE exercise
        SET
            video_status = 'rejected',
            video_review_note = :video_review_note,
            video_reviewed_by = :admin_id
        WHERE exercise_id = :exercise_id
        """,
        params={
            "video_review_note": final_note,
            "admin_id": user_id,
            "exercise_id": int(exercise_id),
        },
        fetch=False,
        commit=True,
    )

    updated = _get_video_target_row(int(exercise_id))
    return _shape_video_row(updated, user_timezone)


def remove_admin_video(user_id: int, exercise_id, user_timezone: str | None = None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not exercise_id:
        raise ValueError("exercise_id is required")

    existing = _get_video_target_row(int(exercise_id))

    if not existing["video_url"]:
        raise ValueError("Exercise has no video to remove")

    run_query(
        """
        UPDATE exercise
        SET
            video_url = NULL,
            video_status = 'rejected',
            video_review_note = COALESCE(video_review_note, 'Video removed by admin'),
            video_reviewed_by = :admin_id
        WHERE exercise_id = :exercise_id
        """,
        params={
            "admin_id": user_id,
            "exercise_id": int(exercise_id),
        },
        fetch=False,
        commit=True,
    )

    updated = _get_video_target_row(int(exercise_id))
    return _shape_video_row(updated, user_timezone)
