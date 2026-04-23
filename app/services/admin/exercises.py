from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _get_exercise_row(exercise_id: int):
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
        params={"exercise_id": exercise_id},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Exercise not found")

    row = rows[0]

    return {
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
    }


def get_admin_exercises(user_id: int):
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
        ORDER BY exercise_id ASC
        """,
        fetch=True,
        commit=False
    )

    exercises = []

    for row in rows:
        exercises.append({
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

    return exercises


def create_admin_exercise(
    user_id: int,
    exercise_name: str,
    equipment=None,
    video_url=None,
    created_by=None
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not exercise_name:
        raise ValueError("exercise_name is required")

    existing_rows = run_query(
        """
        SELECT exercise_id
        FROM exercise
        WHERE exercise_name = :exercise_name
        """,
        params={"exercise_name": exercise_name},
        fetch=True,
        commit=False
    )

    if existing_rows:
        raise ValueError("Exercise with this name already exists")

    final_created_by = int(created_by) if created_by is not None else user_id
    final_video_status = "pending" if video_url else "approved"

    run_query(
        """
        INSERT INTO exercise (
            exercise_name,
            equipment,
            video_url,
            video_status,
            video_review_note,
            video_reviewed_by,
            created_by
        )
        VALUES (
            :exercise_name,
            :equipment,
            :video_url,
            :video_status,
            NULL,
            NULL,
            :created_by
        )
        """,
        params={
            "exercise_name": exercise_name,
            "equipment": equipment,
            "video_url": video_url,
            "video_status": final_video_status,
            "created_by": final_created_by
        },
        fetch=False,
        commit=True
    )

    created_rows = run_query(
        """
        SELECT exercise_id
        FROM exercise
        WHERE exercise_name = :exercise_name
        ORDER BY exercise_id DESC
        LIMIT 1
        """,
        params={"exercise_name": exercise_name},
        fetch=True,
        commit=False
    )

    return _get_exercise_row(created_rows[0]["exercise_id"])


def update_admin_exercise(
    user_id: int,
    exercise_id,
    exercise_name=None,
    equipment=None,
    video_url=None
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not exercise_id:
        raise ValueError("exercise_id is required")

    current = _get_exercise_row(int(exercise_id))

    final_exercise_name = exercise_name if exercise_name is not None else current["exercise_name"]
    final_equipment = equipment if equipment is not None else current["equipment"]
    final_video_url = video_url if video_url is not None else current["video_url"]

    duplicate_rows = run_query(
        """
        SELECT exercise_id
        FROM exercise
        WHERE exercise_name = :exercise_name
          AND exercise_id != :exercise_id
        """,
        params={
            "exercise_name": final_exercise_name,
            "exercise_id": int(exercise_id)
        },
        fetch=True,
        commit=False
    )

    if duplicate_rows:
        raise ValueError("Exercise with this name already exists")

    if video_url is not None and video_url != current["video_url"] and video_url:
        final_video_status = "pending"
        final_video_review_note = None
        final_video_reviewed_by = None
    else:
        final_video_status = current["video_status"]
        final_video_review_note = current["video_review_note"]
        final_video_reviewed_by = current["video_reviewed_by"]

    run_query(
        """
        UPDATE exercise
        SET
            exercise_name = :exercise_name,
            equipment = :equipment,
            video_url = :video_url,
            video_status = :video_status,
            video_review_note = :video_review_note,
            video_reviewed_by = :video_reviewed_by
        WHERE exercise_id = :exercise_id
        """,
        params={
            "exercise_name": final_exercise_name,
            "equipment": final_equipment,
            "video_url": final_video_url,
            "video_status": final_video_status,
            "video_review_note": final_video_review_note,
            "video_reviewed_by": final_video_reviewed_by,
            "exercise_id": int(exercise_id)
        },
        fetch=False,
        commit=True
    )

    return _get_exercise_row(int(exercise_id))


def delete_admin_exercise(user_id: int, exercise_id):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not exercise_id:
        raise ValueError("exercise_id is required")

    _get_exercise_row(int(exercise_id))

    run_query(
        """
        DELETE FROM exercise
        WHERE exercise_id = :exercise_id
        """,
        params={"exercise_id": int(exercise_id)},
        fetch=False,
        commit=True
    )

    return {"message": "success"}