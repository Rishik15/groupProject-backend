from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _get_workout_row(plan_id: int):
    rows = run_query(
        """
        SELECT
            wp.plan_id,
            wp.plan_name,
            wpt.author_user_id,
            wpt.is_public,
            wpt.description,
            COALESCE(COUNT(pe.exercise_id), 0) AS total_exercises,
            wp.created_at,
            wp.updated_at
        FROM workout_plan AS wp
        JOIN workout_plan_template AS wpt
            ON wp.plan_id = wpt.plan_id
        LEFT JOIN workout_day AS wd
            ON wp.plan_id = wd.plan_id
        LEFT JOIN plan_exercise AS pe
            ON wd.day_id = pe.day_id
        WHERE wp.plan_id = :plan_id
        GROUP BY
            wp.plan_id,
            wp.plan_name,
            wpt.author_user_id,
            wpt.is_public,
            wpt.description,
            wp.created_at,
            wp.updated_at
        """,
        params={"plan_id": int(plan_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Workout not found")

    row = rows[0]

    return {
        "plan_id": row["plan_id"],
        "plan_name": row["plan_name"],
        "author_user_id": row["author_user_id"],
        "is_public": int(row["is_public"]),
        "description": row["description"],
        "total_exercises": int(row["total_exercises"]),
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def _get_primary_day_id(plan_id: int):
    rows = run_query(
        """
        SELECT day_id
        FROM workout_day
        WHERE plan_id = :plan_id
        ORDER BY day_order ASC, day_id ASC
        LIMIT 1
        """,
        params={"plan_id": int(plan_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Workout has no day to update")

    return rows[0]["day_id"]


def get_admin_workouts(user_id: int):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            wp.plan_id,
            wp.plan_name,
            wpt.author_user_id,
            wpt.is_public,
            wpt.description,
            COALESCE(COUNT(pe.exercise_id), 0) AS total_exercises,
            wp.created_at,
            wp.updated_at
        FROM workout_plan AS wp
        JOIN workout_plan_template AS wpt
            ON wp.plan_id = wpt.plan_id
        LEFT JOIN workout_day AS wd
            ON wp.plan_id = wd.plan_id
        LEFT JOIN plan_exercise AS pe
            ON wd.day_id = pe.day_id
        GROUP BY
            wp.plan_id,
            wp.plan_name,
            wpt.author_user_id,
            wpt.is_public,
            wpt.description,
            wp.created_at,
            wp.updated_at
        ORDER BY wp.plan_id ASC
        """,
        fetch=True,
        commit=False
    )

    workouts = []

    for row in rows:
        workouts.append({
            "plan_id": row["plan_id"],
            "plan_name": row["plan_name"],
            "author_user_id": row["author_user_id"],
            "is_public": int(row["is_public"]),
            "description": row["description"],
            "total_exercises": int(row["total_exercises"]),
            "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
        })

    return workouts


def create_admin_workout(
    user_id: int,
    plan_name: str,
    description=None,
    author_user_id=None,
    is_public=0,
    exercises=None
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not plan_name:
        raise ValueError("plan_name is required")

    exercises = exercises or []

    if not exercises:
        raise ValueError("At least one exercise is required")

    existing_rows = run_query(
        """
        SELECT plan_id
        FROM workout_plan
        WHERE plan_name = :plan_name
        """,
        params={"plan_name": plan_name},
        fetch=True,
        commit=False
    )

    if existing_rows:
        raise ValueError("Workout with this name already exists")

    final_author_user_id = int(author_user_id) if author_user_id is not None else user_id
    final_is_public = 1 if int(is_public) == 1 else 0

    author_rows = run_query(
        """
        SELECT user_id
        FROM users_immutables
        WHERE user_id = :user_id
        """,
        params={"user_id": final_author_user_id},
        fetch=True,
        commit=False
    )

    if not author_rows:
        raise ValueError("author_user_id is invalid")

    for ex in exercises:
        exercise_id = ex.get("exercise_id")
        if not exercise_id:
            raise ValueError("Each exercise must include exercise_id")

        exercise_rows = run_query(
            """
            SELECT exercise_id
            FROM exercise
            WHERE exercise_id = :exercise_id
            """,
            params={"exercise_id": int(exercise_id)},
            fetch=True,
            commit=False
        )

        if not exercise_rows:
            raise ValueError(f"Exercise not found: {exercise_id}")

    run_query(
        """
        INSERT INTO workout_plan (plan_name)
        VALUES (:plan_name)
        """,
        params={"plan_name": plan_name},
        fetch=False,
        commit=True
    )

    plan_rows = run_query(
        """
        SELECT plan_id
        FROM workout_plan
        WHERE plan_name = :plan_name
        ORDER BY plan_id DESC
        LIMIT 1
        """,
        params={"plan_name": plan_name},
        fetch=True,
        commit=False
    )

    plan_id = plan_rows[0]["plan_id"]

    run_query(
        """
        INSERT INTO workout_plan_template (
            plan_id,
            author_user_id,
            is_public,
            description
        )
        VALUES (
            :plan_id,
            :author_user_id,
            :is_public,
            :description
        )
        """,
        params={
            "plan_id": plan_id,
            "author_user_id": final_author_user_id,
            "is_public": final_is_public,
            "description": description
        },
        fetch=False,
        commit=True
    )

    run_query(
        """
        INSERT INTO workout_day (
            plan_id,
            day_order,
            day_label
        )
        VALUES (
            :plan_id,
            1,
            'Day 1'
        )
        """,
        params={"plan_id": plan_id},
        fetch=False,
        commit=True
    )

    day_rows = run_query(
        """
        SELECT day_id
        FROM workout_day
        WHERE plan_id = :plan_id
          AND day_order = 1
        LIMIT 1
        """,
        params={"plan_id": plan_id},
        fetch=True,
        commit=False
    )

    day_id = day_rows[0]["day_id"]

    for index, ex in enumerate(exercises):
        run_query(
            """
            INSERT INTO plan_exercise (
                day_id,
                exercise_id,
                order_in_workout,
                sets_goal,
                reps_goal
            )
            VALUES (
                :day_id,
                :exercise_id,
                :order_in_workout,
                :sets_goal,
                :reps_goal
            )
            """,
            params={
                "day_id": day_id,
                "exercise_id": int(ex["exercise_id"]),
                "order_in_workout": index + 1,
                "sets_goal": ex.get("sets"),
                "reps_goal": ex.get("reps")
            },
            fetch=False,
            commit=True
        )

    return _get_workout_row(plan_id)


def update_admin_workout(
    user_id: int,
    plan_id,
    plan_name=None,
    description=None,
    is_public=None
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not plan_id:
        raise ValueError("plan_id is required")

    current = _get_workout_row(int(plan_id))

    final_plan_name = plan_name if plan_name is not None else current["plan_name"]
    final_description = description if description is not None else current["description"]
    final_is_public = int(is_public) if is_public is not None else current["is_public"]

    duplicate_rows = run_query(
        """
        SELECT plan_id
        FROM workout_plan
        WHERE plan_name = :plan_name
          AND plan_id != :plan_id
        """,
        params={
            "plan_name": final_plan_name,
            "plan_id": int(plan_id)
        },
        fetch=True,
        commit=False
    )

    if duplicate_rows:
        raise ValueError("Workout with this name already exists")

    run_query(
        """
        UPDATE workout_plan
        SET
            plan_name = :plan_name
        WHERE plan_id = :plan_id
        """,
        params={
            "plan_name": final_plan_name,
            "plan_id": int(plan_id)
        },
        fetch=False,
        commit=True
    )

    run_query(
        """
        UPDATE workout_plan_template
        SET
            description = :description,
            is_public = :is_public
        WHERE plan_id = :plan_id
        """,
        params={
            "description": final_description,
            "is_public": 1 if int(final_is_public) == 1 else 0,
            "plan_id": int(plan_id)
        },
        fetch=False,
        commit=True
    )

    return _get_workout_row(int(plan_id))


def delete_admin_workout(user_id: int, plan_id):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not plan_id:
        raise ValueError("plan_id is required")

    _get_workout_row(int(plan_id))

    run_query(
        """
        DELETE FROM workout_plan
        WHERE plan_id = :plan_id
        """,
        params={"plan_id": int(plan_id)},
        fetch=False,
        commit=True
    )

    return {"message": "success"}


def update_admin_workout_exercises(user_id: int, plan_id, exercises=None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not plan_id:
        raise ValueError("plan_id is required")

    exercises = exercises or []

    if not exercises:
        raise ValueError("At least one exercise is required")

    _get_workout_row(int(plan_id))
    day_id = _get_primary_day_id(int(plan_id))

    for ex in exercises:
        exercise_id = ex.get("exercise_id")
        if not exercise_id:
            raise ValueError("Each exercise must include exercise_id")

        exercise_rows = run_query(
            """
            SELECT exercise_id
            FROM exercise
            WHERE exercise_id = :exercise_id
            """,
            params={"exercise_id": int(exercise_id)},
            fetch=True,
            commit=False
        )

        if not exercise_rows:
            raise ValueError(f"Exercise not found: {exercise_id}")

    run_query(
        """
        DELETE FROM plan_exercise
        WHERE day_id = :day_id
        """,
        params={"day_id": int(day_id)},
        fetch=False,
        commit=True
    )

    for index, ex in enumerate(exercises):
        run_query(
            """
            INSERT INTO plan_exercise (
                day_id,
                exercise_id,
                order_in_workout,
                sets_goal,
                reps_goal
            )
            VALUES (
                :day_id,
                :exercise_id,
                :order_in_workout,
                :sets_goal,
                :reps_goal
            )
            """,
            params={
                "day_id": int(day_id),
                "exercise_id": int(ex["exercise_id"]),
                "order_in_workout": index + 1,
                "sets_goal": ex.get("sets"),
                "reps_goal": ex.get("reps")
            },
            fetch=False,
            commit=True
        )

    return _get_workout_row(int(plan_id))