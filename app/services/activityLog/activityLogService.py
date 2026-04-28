from app.services import run_query


def _to_int(value):
    if value is None or value == "":
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _to_float(value):
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _format_datetime(value):
    if value is None:
        return None

    return str(value)


def _session_belongs_to_user(user_id: int, session_id: int):
    rows = run_query(
        """
        SELECT
            session_id,
            ended_at
        FROM workout_session
        WHERE session_id = :session_id
        AND user_id = :user_id
        LIMIT 1
        """,
        {
            "session_id": session_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    return rows[0]


def _format_strength_logs(rows):
    strength_logs = []

    for row in rows:
        strength_logs.append(
            {
                "setLogId": row["set_log_id"],
                "sessionId": row["session_id"],
                "exerciseId": row["exercise_id"],
                "exerciseName": row["exercise_name"],
                "setNumber": row["set_number"],
                "reps": row["reps"],
                "weight": float(row["weight"]) if row["weight"] is not None else None,
                "rpe": float(row["rpe"]) if row["rpe"] is not None else None,
                "performedAt": _format_datetime(row["performed_at"]),
                "startedAt": _format_datetime(row.get("started_at")),
                "endedAt": _format_datetime(row.get("ended_at")),
                "workoutPlanName": row.get("plan_name"),
                "workoutDayLabel": row.get("day_label"),
                "canEdit": bool(row["can_edit"]),
            }
        )

    return strength_logs


def _format_cardio_logs(rows):
    cardio_logs = []

    for row in rows:
        cardio_logs.append(
            {
                "cardioLogId": row["cardio_log_id"],
                "sessionId": row["session_id"],
                "userId": row["user_id"],
                "performedAt": _format_datetime(row["performed_at"]),
                "steps": row["steps"],
                "distanceKm": (
                    float(row["distance_km"])
                    if row["distance_km"] is not None
                    else None
                ),
                "durationMin": row["duration_min"],
                "calories": row["calories"],
                "avgHr": row["avg_hr"],
                "canEdit": bool(row["can_edit"]),
            }
        )

    return cardio_logs


def get_activity_logs(user_id: int, session_id: int | None = None):
    if session_id:
        session_row = _session_belongs_to_user(user_id, session_id)

        if not session_row:
            return {
                "success": False,
                "reason": "not_found",
                "message": "Session was not found.",
            }

    strength_query = """
        SELECT
            esl.set_log_id,
            esl.session_id,
            esl.exercise_id,
            e.exercise_name,
            esl.set_number,
            esl.reps,
            esl.weight,
            esl.rpe,
            esl.performed_at,
            ws.started_at,
            ws.ended_at,
            wp.plan_name,
            wd.day_label,
            CASE
                WHEN esl.performed_at >= CURDATE()
                AND esl.performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                THEN 1
                ELSE 0
            END AS can_edit
        FROM exercise_set_log esl
        JOIN exercise e
            ON e.exercise_id = esl.exercise_id
        JOIN workout_session ws
            ON ws.session_id = esl.session_id
        LEFT JOIN workout_plan wp
            ON wp.plan_id = ws.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = ws.workout_day_id
        WHERE ws.user_id = :user_id
        AND esl.performed_at >= CURDATE()
        AND esl.performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
    """

    strength_params = {"user_id": user_id}

    if session_id:
        strength_query += " AND esl.session_id = :session_id"
        strength_params["session_id"] = session_id

    strength_query += " ORDER BY esl.performed_at DESC, esl.set_number ASC"

    strength_rows = run_query(
        strength_query,
        strength_params,
        fetch=True,
        commit=False,
    )

    cardio_query = """
        SELECT
            cardio_log_id,
            session_id,
            user_id,
            performed_at,
            steps,
            distance_km,
            duration_min,
            calories,
            avg_hr,
            CASE
                WHEN performed_at >= CURDATE()
                AND performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                THEN 1
                ELSE 0
            END AS can_edit
        FROM cardio_log
        WHERE user_id = :user_id
        AND performed_at >= CURDATE()
        AND performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
    """

    cardio_params = {"user_id": user_id}

    if session_id:
        cardio_query += " AND session_id = :session_id"
        cardio_params["session_id"] = session_id

    cardio_query += " ORDER BY performed_at DESC"

    cardio_rows = run_query(
        cardio_query,
        cardio_params,
        fetch=True,
        commit=False,
    )

    return {
        "success": True,
        "sessionId": session_id,
        "strengthLogs": _format_strength_logs(strength_rows),
        "cardioLogs": _format_cardio_logs(cardio_rows),
    }


def get_full_activity_logs(user_id: int):
    strength_rows = run_query(
        """
        SELECT
            esl.set_log_id,
            esl.session_id,
            esl.exercise_id,
            e.exercise_name,
            esl.set_number,
            esl.reps,
            esl.weight,
            esl.rpe,
            esl.performed_at,
            ws.started_at,
            ws.ended_at,
            wp.plan_name,
            wd.day_label,
            CASE
                WHEN esl.performed_at >= CURDATE()
                AND esl.performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                THEN 1
                ELSE 0
            END AS can_edit
        FROM exercise_set_log esl
        JOIN exercise e
            ON e.exercise_id = esl.exercise_id
        JOIN workout_session ws
            ON ws.session_id = esl.session_id
        LEFT JOIN workout_plan wp
            ON wp.plan_id = ws.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = ws.workout_day_id
        WHERE ws.user_id = :user_id
        ORDER BY esl.performed_at DESC, esl.set_log_id DESC
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    cardio_rows = run_query(
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
            avg_hr,
            CASE
                WHEN performed_at >= CURDATE()
                AND performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                THEN 1
                ELSE 0
            END AS can_edit
        FROM cardio_log
        WHERE user_id = :user_id
        ORDER BY performed_at DESC, cardio_log_id DESC
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return {
        "success": True,
        "strengthLogs": _format_strength_logs(strength_rows),
        "cardioLogs": _format_cardio_logs(cardio_rows),
    }


def log_strength_set(user_id: int, data: dict):
    session_id = _to_int(data.get("session_id"))
    exercise_id = _to_int(data.get("exercise_id"))
    set_number = _to_int(data.get("set_number"))
    reps = _to_int(data.get("reps"))
    weight = _to_float(data.get("weight"))
    rpe = _to_float(data.get("rpe"))

    if not session_id:
        return {
            "success": False,
            "reason": "missing_session",
            "message": "Start a workout session before logging exercises.",
        }

    if not exercise_id:
        return {
            "success": False,
            "reason": "missing_exercise",
            "message": "exercise_id is required.",
        }

    if not set_number:
        return {
            "success": False,
            "reason": "missing_set_number",
            "message": "set_number is required.",
        }

    session_row = _session_belongs_to_user(user_id, session_id)

    if not session_row:
        return {
            "success": False,
            "reason": "not_found",
            "message": "Session was not found.",
        }

    if session_row["ended_at"] is not None:
        return {
            "success": False,
            "reason": "session_finished",
            "message": "This workout session is already finished.",
        }

    exercise_rows = run_query(
        """
        SELECT exercise_id
        FROM exercise
        WHERE exercise_id = :exercise_id
        LIMIT 1
        """,
        {"exercise_id": exercise_id},
        fetch=True,
        commit=False,
    )

    if not exercise_rows:
        return {
            "success": False,
            "reason": "exercise_not_found",
            "message": "Exercise was not found.",
        }

    set_log_id = run_query(
        """
        INSERT INTO exercise_set_log (
            session_id,
            exercise_id,
            set_number,
            reps,
            weight,
            rpe,
            performed_at
        )
        VALUES (
            :session_id,
            :exercise_id,
            :set_number,
            :reps,
            :weight,
            :rpe,
            NOW()
        )
        """,
        {
            "session_id": session_id,
            "exercise_id": exercise_id,
            "set_number": set_number,
            "reps": reps,
            "weight": weight,
            "rpe": rpe,
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    return {
        "success": True,
        "message": "Strength set logged.",
        "setLogId": set_log_id,
    }


def update_strength_set(user_id: int, set_log_id: int, data: dict):
    set_number = _to_int(data.get("set_number"))
    reps = _to_int(data.get("reps"))
    weight = _to_float(data.get("weight"))
    rpe = _to_float(data.get("rpe"))

    if not set_number:
        return {
            "success": False,
            "reason": "missing_set_number",
            "message": "set_number is required.",
        }

    existing_rows = run_query(
        """
        SELECT
            esl.set_log_id
        FROM exercise_set_log esl
        JOIN workout_session ws
            ON ws.session_id = esl.session_id
        WHERE esl.set_log_id = :set_log_id
        AND ws.user_id = :user_id
        LIMIT 1
        """,
        {
            "set_log_id": set_log_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not existing_rows:
        return {
            "success": False,
            "reason": "not_found",
            "message": "Strength log was not found.",
        }

    updated_rows = run_query(
        """
        UPDATE exercise_set_log esl
        JOIN workout_session ws
            ON ws.session_id = esl.session_id
        SET
            esl.set_number = :set_number,
            esl.reps = :reps,
            esl.weight = :weight,
            esl.rpe = :rpe
        WHERE esl.set_log_id = :set_log_id
        AND ws.user_id = :user_id
        AND esl.performed_at >= CURDATE()
        AND esl.performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
        """,
        {
            "set_log_id": set_log_id,
            "user_id": user_id,
            "set_number": set_number,
            "reps": reps,
            "weight": weight,
            "rpe": rpe,
        },
        fetch=False,
        commit=True,
    )

    if updated_rows == 0:
        return {
            "success": False,
            "reason": "not_editable",
            "message": "Only today's logs can be edited.",
        }

    return {
        "success": True,
        "message": "Strength log updated.",
        "setLogId": set_log_id,
    }


def log_cardio_activity(user_id: int, data: dict):
    session_id = _to_int(data.get("session_id"))
    steps = _to_int(data.get("steps"))
    distance_km = _to_float(data.get("distance_km"))
    duration_min = _to_int(data.get("duration_min"))
    calories = _to_int(data.get("calories"))
    avg_hr = _to_int(data.get("avg_hr"))

    if session_id:
        session_row = _session_belongs_to_user(user_id, session_id)

        if not session_row:
            return {
                "success": False,
                "reason": "not_found",
                "message": "Session was not found.",
            }

        if session_row["ended_at"] is not None:
            return {
                "success": False,
                "reason": "session_finished",
                "message": "This workout session is already finished.",
            }

    if (
        steps is None
        and distance_km is None
        and duration_min is None
        and calories is None
        and avg_hr is None
    ):
        return {
            "success": False,
            "reason": "empty_log",
            "message": "Enter at least one cardio value.",
        }

    cardio_log_id = run_query(
        """
        INSERT INTO cardio_log (
            session_id,
            user_id,
            performed_at,
            steps,
            distance_km,
            duration_min,
            calories,
            avg_hr
        )
        VALUES (
            :session_id,
            :user_id,
            NOW(),
            :steps,
            :distance_km,
            :duration_min,
            :calories,
            :avg_hr
        )
        """,
        {
            "session_id": session_id,
            "user_id": user_id,
            "steps": steps,
            "distance_km": distance_km,
            "duration_min": duration_min,
            "calories": calories,
            "avg_hr": avg_hr,
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    return {
        "success": True,
        "message": "Cardio activity logged.",
        "cardioLogId": cardio_log_id,
    }


def update_cardio_log(user_id: int, cardio_log_id: int, data: dict):
    steps = _to_int(data.get("steps"))
    distance_km = _to_float(data.get("distance_km"))
    duration_min = _to_int(data.get("duration_min"))
    calories = _to_int(data.get("calories"))
    avg_hr = _to_int(data.get("avg_hr"))

    if (
        steps is None
        and distance_km is None
        and duration_min is None
        and calories is None
        and avg_hr is None
    ):
        return {
            "success": False,
            "reason": "empty_log",
            "message": "Enter at least one cardio value.",
        }

    existing_rows = run_query(
        """
        SELECT cardio_log_id
        FROM cardio_log
        WHERE cardio_log_id = :cardio_log_id
        AND user_id = :user_id
        LIMIT 1
        """,
        {
            "cardio_log_id": cardio_log_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not existing_rows:
        return {
            "success": False,
            "reason": "not_found",
            "message": "Cardio log was not found.",
        }

    updated_rows = run_query(
        """
        UPDATE cardio_log
        SET
            steps = :steps,
            distance_km = :distance_km,
            duration_min = :duration_min,
            calories = :calories,
            avg_hr = :avg_hr
        WHERE cardio_log_id = :cardio_log_id
        AND user_id = :user_id
        AND performed_at >= CURDATE()
        AND performed_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
        """,
        {
            "cardio_log_id": cardio_log_id,
            "user_id": user_id,
            "steps": steps,
            "distance_km": distance_km,
            "duration_min": duration_min,
            "calories": calories,
            "avg_hr": avg_hr,
        },
        fetch=False,
        commit=True,
    )

    if updated_rows == 0:
        return {
            "success": False,
            "reason": "not_editable",
            "message": "Only today's logs can be edited.",
        }

    return {
        "success": True,
        "message": "Cardio log updated.",
        "cardioLogId": cardio_log_id,
    }
