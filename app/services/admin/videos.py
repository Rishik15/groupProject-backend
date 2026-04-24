from app.services import run_query
from app.services.admin.dashboard import _is_admin


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
        commit=False
    )

    if not rows:
        raise ValueError("Exercise not found")

    return rows[0]


def _shape_video_row(row):
    return {
        "exercise_id": row["exercise_id"],
        "exercise_name": row.get("exercise_name"),
        "equipment": row.get("equipment"),
        "video_url": row["video_url"],
        "video_status": row["video_status"],
        "video_review_note": row["video_review_note"],
        "video_reviewed_by": row["video_reviewed_by"],
        "created_by": row.get("created_by"),
        "created_at": row["created_at"].isoformat() if row.get("created_at") is not None else None,
        "updated_at": row["updated_at"].isoformat() if row.get("updated_at") is not None else None,
    }


def get_pending_admin_videos(user_id: int):
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
        commit=False
    )

    videos = []

    for row in rows:
        videos.append({
            "exercise_id": row["exercise_id"],
            "exercise_name": row["exercise_name"],
            "equipment": row["equipment"],
            "video_url": row["video_url"],
            "video_status": row["video_status"],
            "video_review_note": row["video_review_note"],
            "video_reviewed_by": row["video_reviewed_by"],
            "created_by": row["created_by"],
            "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
        })

    return videos


def approve_admin_video(user_id: int, exercise_id):
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
            "exercise_id": int(exercise_id)
        },
        fetch=False,
        commit=True
    )

    updated = _get_video_target_row(int(exercise_id))
    return _shape_video_row(updated)


def reject_admin_video(user_id: int, exercise_id, video_review_note=None):
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
            "exercise_id": int(exercise_id)
        },
        fetch=False,
        commit=True
    )

    updated = _get_video_target_row(int(exercise_id))
    return _shape_video_row(updated)


def remove_admin_video(user_id: int, exercise_id):
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
            "exercise_id": int(exercise_id)
        },
        fetch=False,
        commit=True
    )

    updated = _get_video_target_row(int(exercise_id))
    return _shape_video_row(updated)