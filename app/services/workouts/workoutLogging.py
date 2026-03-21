from app.services import run_query
from datetime import datetime


def startWorkoutSession(user_id: int, workout_plan_id: int | None = None, notes: str | None = None):
    started_at = datetime.now()

    run_query(
        """
        INSERT INTO workout_session
            (
                user_id,
                started_at,
                workout_plan_id,
                notes
            )
        VALUES
            (
                :uid,
                :started_at,
                :plan_id,
                :notes
            );
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
        SELECT
            session_id,
            user_id,
            started_at,
            ended_at,
            workout_plan_id,
            notes
        FROM workout_session
        WHERE user_id = :uid
          AND started_at = :started_at
        ORDER BY session_id DESC
        LIMIT 1;
        """,
        {
            "uid": user_id,
            "started_at": started_at
        },
        fetch=True,
        commit=False
    )

    return rows[0] if rows else None


def getWorkoutSessionById(user_id: int, session_id: int):
    rows = run_query(
        """
        SELECT
            session_id,
            user_id,
            started_at,
            ended_at,
            workout_plan_id,
            notes
        FROM workout_session
        WHERE session_id = :sid
          AND user_id = :uid
        LIMIT 1;
        """,
        {
            "sid": session_id,
            "uid": user_id
        }
    )

    return rows[0] if rows else None


def getActiveWorkoutSession(user_id: int):
    rows = run_query(
        """
        SELECT
            session_id,
            user_id,
            started_at,
            ended_at,
            workout_plan_id,
            notes
        FROM workout_session
        WHERE user_id = :uid
          AND ended_at IS NULL
        ORDER BY started_at DESC, session_id DESC
        LIMIT 1;
        """,
        {
            "uid": user_id
        }
    )

    return rows[0] if rows else None


def sessionBelongsToUser(user_id: int, session_id: int) -> bool:
    rows = run_query(
        """
        SELECT session_id
        FROM workout_session
        WHERE session_id = :sid
          AND user_id = :uid
        LIMIT 1;
        """,
        {
            "sid": session_id,
            "uid": user_id
        }
    )
    return len(rows) > 0


def sessionIsOpen(user_id: int, session_id: int) -> bool:
    rows = run_query(
        """
        SELECT session_id
        FROM workout_session
        WHERE session_id = :sid
          AND user_id = :uid
          AND ended_at IS NULL
        LIMIT 1;
        """,
        {
            "sid": session_id,
            "uid": user_id
        }
    )
    return len(rows) > 0


def endWorkoutSession(user_id: int, session_id: int):
    if not sessionBelongsToUser(user_id, session_id):
        return {"success": False, "reason": "session does not belong to user"}

    if not sessionIsOpen(user_id, session_id):
        return {"success": False, "reason": "already_ended"}

    run_query(
        """
        UPDATE workout_session
        SET ended_at = :date
        WHERE user_id = :uid AND session_id = :sid;
        """,
        {
            "date": datetime.now(),
            "uid": user_id,
            "sid": session_id
        },
        fetch=False,
        commit=True
    )

    return {"success": True}


def logWorkoutInformation(
    user_id: int,
    session_id: int,
    exercise_id: int,
    set_number: int,
    reps: int | None,
    weight: float | None,
    rpe: float | None,
    datetimeFinished=None,
):
    if not sessionBelongsToUser(user_id, session_id):
        return {"success": False, "reason": "session does not belong to user"}

    if not sessionIsOpen(user_id, session_id):
        return {"success": False, "reason": "ended"}

    d = datetime.now() if datetimeFinished is None else datetimeFinished

    run_query(
        """
        INSERT INTO exercise_set_log
            (
                session_id,
                exercise_id,
                set_number,
                reps,
                weight,
                rpe,
                performed_at
            )
        VALUES
            (
                :sid,
                :eid,
                :set_n,
                :reps,
                :weight,
                :rpe,
                :date
            );
        """,
        {
            "date": d,
            "sid": session_id,
            "eid": exercise_id,
            "set_n": set_number,
            "reps": reps,
            "weight": weight,
            "rpe": rpe
        },
        fetch=False,
        commit=True
    )

    return {"success": True}


def logCardioActivity(
    user_id: int,
    session_id: int | None = None,
    performed_at=None,
    steps: int | None = None,
    distance_km: float | None = None,
    duration_min: int | None = None,
    calories: int | None = None,
    avg_hr: int | None = None,
):
    if session_id is not None:
        if not sessionBelongsToUser(user_id, session_id):
            return {"success": False, "reason": "session does not belong to user"}  

        if not sessionIsOpen(user_id, session_id):
            return {"success": False, "reason": "ended"}

    p_at = datetime.now() if performed_at is None else performed_at

    run_query(
        """
        INSERT INTO cardio_log
            (
                session_id,
                user_id,
                performed_at,
                steps,
                distance_km,
                duration_min,
                calories,
                avg_hr
            )
        VALUES
            (
                :sid,
                :uid,
                :performed_at,
                :steps,
                :distance_km,
                :duration_min,
                :calories,
                :avg_hr
            );
        """,
        {
            "sid": session_id,
            "uid": user_id,
            "performed_at": p_at,
            "steps": steps,
            "distance_km": distance_km,
            "duration_min": duration_min,
            "calories": calories,
            "avg_hr": avg_hr
        },
        fetch=False,
        commit=True
    )

    return {"success": True}


def getSessionSets(user_id: int, session_id: int):
    if not sessionBelongsToUser(user_id, session_id):
        return {"success": False, "reason": "session does not belong to user"}

    return run_query(
        """
        SELECT
            set_log_id,
            session_id,
            exercise_id,
            set_number,
            reps,
            weight,
            rpe,
            performed_at
        FROM exercise_set_log
        WHERE session_id = :sid
        ORDER BY exercise_id ASC, set_number ASC, performed_at ASC;
        """,
        {
            "sid": session_id
        }
    )


def getSessionCardio(user_id: int, session_id: int):
    if not sessionBelongsToUser(user_id, session_id):
        return {"success": False, "reason": "session does not belong to user"}

    return run_query(
        """
        SELECT
            cardio_log_id,
            session_id,
            user_id,
            performed_at,
            steps,
            distance_km,
            duration_min,
            calories,
            avg_hr
        FROM cardio_log
        WHERE session_id = :sid
          AND user_id = :uid
        ORDER BY performed_at ASC, cardio_log_id ASC;
        """,
        {
            "sid": session_id,
            "uid": user_id
        }
    )