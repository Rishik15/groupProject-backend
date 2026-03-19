from app.services import run_query
from datetime import datetime


def endWorkoutSession(user_id: int, session_id: int):
    try:
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
            }
        )
    except Exception as e:
        raise e


def logWorkoutInformation(
    session_id: int,
    exercise_id: int,
    set_number: int,
    reps: int | None,
    weight: float | None,
    rpe: float | None,
    datetimeFinished=None,
):
    try:
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
            }
        )
    except Exception as e:
        raise e