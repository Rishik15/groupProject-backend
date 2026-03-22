from app.services import run_query
from datetime import datetime
from . import workoutActionsFuncs 

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
    try:
        if not workoutActionsFuncs.sessionBelongsToUser(user_id, session_id):
            return {"success": False, "reason": "not_found"}

        if not workoutActionsFuncs.sessionIsOpen(user_id, session_id):
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

    except Exception:
        raise Exception("Failed to log workout information")


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
    try:
        if session_id is not None:
            if not workoutActionsFuncs.sessionBelongsToUser(user_id, session_id):
                return {"success": False, "reason": "not_found"}

            if not workoutActionsFuncs.sessionIsOpen(user_id, session_id):
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

    except Exception:
        raise Exception("Failed to log cardio activity")
