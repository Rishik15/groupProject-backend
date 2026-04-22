# app/services/workouts/workoutActionsFuncs.py
from app.services import run_query
from datetime import datetime


def get_ExerciseInfo(plan_id: int):
    try:
        ret = run_query(
            """
            SELECT
                pe.exercise_id,
                pe.order_in_workout,
                pe.sets_goal,
                pe.reps_goal,
                pe.weight_goal,
                e.exercise_name,
                e.equipment,
                e.video_url,
                wd.day_order,
                wd.day_label
            FROM workout_day wd
            JOIN plan_exercise pe ON pe.day_id = wd.day_id
            JOIN exercise e ON pe.exercise_id = e.exercise_id
            WHERE wd.plan_id = :p_id
            ORDER BY wd.day_order ASC, pe.order_in_workout ASC
            """,
            {"p_id": plan_id},
            fetch=True,
            commit=False
        )

        return ret if ret else []

    except Exception:
        raise Exception("Failed to fetch exercise info")


def getPlanNamesAndIds(user_id: int):
    try:
        ret = run_query(
            """
            SELECT
                ws.session_id,
                ws.workout_plan_id,
                wp.plan_name
            FROM workout_session ws
            JOIN workout_plan wp ON ws.workout_plan_id = wp.plan_id
            WHERE ws.user_id = :u_id
            """,
            {"u_id": user_id},
            fetch=True,
            commit=False
        )

        return ret if ret else []

    except Exception:
        raise Exception("Failed to fetch plan names and ids")


def startWorkoutSession(user_id: int, workout_plan_id: int | None = None, notes: str | None = None):
    try:
        started_at = datetime.now()

        run_query(
            """
            INSERT INTO workout_session (user_id, started_at, workout_plan_id, notes)
            VALUES (:uid, :started_at, :plan_id, :notes)
            """,
            {
                "uid": user_id,
                "started_at": started_at,
                "plan_id": workout_plan_id,
                "notes": notes
            },
            fetch=False,
            commit=True
        )

        rows = run_query(
            """
            SELECT session_id, user_id, started_at, ended_at, workout_plan_id, notes
            FROM workout_session
            WHERE user_id = :uid AND started_at = :started_at
            ORDER BY session_id DESC
            LIMIT 1
            """,
            {"uid": user_id, "started_at": started_at},
            fetch=True,
            commit=False
        )

        return rows[0] if rows else None

    except Exception:
        raise Exception("Failed to start workout session")


def getWorkoutSessionById(user_id: int, session_id: int):
    try:
        rows = run_query(
            """
            SELECT session_id, user_id, started_at, ended_at, workout_plan_id, notes
            FROM workout_session
            WHERE session_id = :sid AND user_id = :uid
            LIMIT 1
            """,
            {"sid": session_id, "uid": user_id}
        )

        return rows[0] if rows else None

    except Exception:
        raise Exception("Failed to fetch workout session")


def getActiveWorkoutSession(user_id: int):
    try:
        rows = run_query(
            """
            SELECT session_id, user_id, started_at, ended_at, workout_plan_id, notes
            FROM workout_session
            WHERE user_id = :uid AND ended_at IS NULL
            ORDER BY started_at DESC, session_id DESC
            LIMIT 1
            """,
            {"uid": user_id}
        )

        return rows[0] if rows else None

    except Exception:
        raise Exception("Failed to fetch active workout session")


def sessionBelongsToUser(user_id: int, session_id: int) -> bool:
    try:
        rows = run_query(
            """
            SELECT session_id FROM workout_session
            WHERE session_id = :sid AND user_id = :uid
            LIMIT 1
            """,
            {"sid": session_id, "uid": user_id}
        )
        return len(rows) > 0

    except Exception:
        raise Exception("Failed to validate workout session ownership")


def sessionIsOpen(user_id: int, session_id: int) -> bool:
    try:
        rows = run_query(
            """
            SELECT session_id FROM workout_session
            WHERE session_id = :sid AND user_id = :uid AND ended_at IS NULL
            LIMIT 1
            """,
            {"sid": session_id, "uid": user_id}
        )
        return len(rows) > 0

    except Exception:
        raise Exception("Failed to validate workout session status")


def endWorkoutSession(user_id: int, session_id: int):
    try:
        if not sessionBelongsToUser(user_id, session_id):
            return {"success": False, "reason": "not_found"}

        if not sessionIsOpen(user_id, session_id):
            return {"success": False, "reason": "already_ended"}

        run_query(
            """
            UPDATE workout_session
            SET ended_at = :date
            WHERE user_id = :uid AND session_id = :sid
            """,
            {"date": datetime.now(), "uid": user_id, "sid": session_id},
            fetch=False,
            commit=True
        )

        return {"success": True}

    except Exception:
        raise Exception("Failed to end workout session")


def getSessionSets(user_id: int, session_id: int):
    try:
        if not sessionBelongsToUser(user_id, session_id):
            return {"success": False, "reason": "not_found"}

        return run_query(
            """
            SELECT
                set_log_id, session_id, exercise_id,
                set_number, reps, weight, rpe, performed_at
            FROM exercise_set_log
            WHERE session_id = :sid
            ORDER BY exercise_id ASC, set_number ASC, performed_at ASC
            """,
            {"sid": session_id}
        )

    except Exception:
        raise Exception("Failed to fetch workout sets")


def getSessionCardio(user_id: int, session_id: int):
    try:
        if not sessionBelongsToUser(user_id, session_id):
            return {"success": False, "reason": "not_found"}

        return run_query(
            """
            SELECT
                cardio_log_id, session_id, user_id, performed_at,
                steps, distance_km, duration_min, calories, avg_hr
            FROM cardio_log
            WHERE session_id = :sid AND user_id = :uid
            ORDER BY performed_at ASC, cardio_log_id ASC
            """,
            {"sid": session_id, "uid": user_id}
        )

    except Exception:
        raise Exception("Failed to fetch cardio logs")