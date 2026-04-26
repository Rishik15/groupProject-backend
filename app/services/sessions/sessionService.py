from app.services import run_query


def _format_time(value):
    if value is None:
        return None

    return str(value)


def _format_datetime(value):
    if value is None:
        return None

    return str(value)


def _get_session_status(row):
    session_id = row.get("session_id")
    ended_at = row.get("ended_at")
    end_time = row.get("end_time")
    server_time = row.get("server_time")

    if session_id and ended_at is None:
        return "active"

    if session_id and ended_at is not None:
        return "completed"

    if end_time and server_time and end_time < server_time:
        return "missed"

    return "not_started"


def _map_scheduled_event(row):
    status = _get_session_status(row)

    return {
        "eventId": row["event_id"],
        "title": row["description"] or "Workout Session",
        "date": str(row["event_date"]),
        "startTime": _format_time(row["start_time"]),
        "endTime": _format_time(row["end_time"]),
        "workoutPlanId": row["workout_plan_id"],
        "workoutPlanName": row["workout_plan_name"],
        "workoutDayId": row["workout_day_id"],
        "workoutDayLabel": row["workout_day_label"],
        "workoutDayOrder": row["workout_day_order"],
        "sessionId": row["session_id"],
        "sessionStatus": status,
        "canStart": status in ["not_started", "missed"],
    }


def _map_active_session(row):
    if not row:
        return None

    return {
        "sessionId": row["session_id"],
        "eventId": row["event_id"],
        "workoutPlanId": row["workout_plan_id"],
        "workoutPlanName": row["workout_plan_name"],
        "workoutDayId": row["workout_day_id"],
        "workoutDayLabel": row["workout_day_label"],
        "title": row["title"],
        "startedAt": _format_datetime(row["started_at"]),
        "endedAt": _format_datetime(row["ended_at"]),
        "notes": row["notes"],
    }


def get_today_scheduled_sessions(user_id: int):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.user_id,
            e.event_date,
            e.start_time,
            e.end_time,
            e.description,
            e.notes,
            e.workout_plan_id,
            e.workout_day_id,
            wp.plan_name AS workout_plan_name,
            wd.day_label AS workout_day_label,
            wd.day_order AS workout_day_order,
            ws.session_id,
            ws.started_at,
            ws.ended_at,
            CURTIME() AS server_time
        FROM event e
        LEFT JOIN workout_plan wp
            ON wp.plan_id = e.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = e.workout_day_id
        LEFT JOIN workout_session ws
            ON ws.event_id = e.event_id
            AND ws.user_id = e.user_id
        WHERE e.user_id = :user_id
        AND e.event_type = 'workout'
        AND e.event_date = CURDATE()
        ORDER BY e.start_time ASC, e.event_id ASC
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    events = [_map_scheduled_event(row) for row in rows]

    return {
        "success": True,
        "events": events,
    }


def get_active_session(user_id: int):
    rows = run_query(
        """
        SELECT
            ws.session_id,
            ws.user_id,
            ws.event_id,
            ws.workout_plan_id,
            ws.workout_day_id,
            ws.started_at,
            ws.ended_at,
            ws.notes,
            e.description AS title,
            wp.plan_name AS workout_plan_name,
            wd.day_label AS workout_day_label
        FROM workout_session ws
        LEFT JOIN event e
            ON e.event_id = ws.event_id
        LEFT JOIN workout_plan wp
            ON wp.plan_id = ws.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = ws.workout_day_id
        WHERE ws.user_id = :user_id
        AND ws.ended_at IS NULL
        ORDER BY ws.started_at DESC
        LIMIT 1
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    active_session = _map_active_session(rows[0]) if rows else None

    return {
        "success": True,
        "session": active_session,
    }


def start_scheduled_session(user_id: int, event_id: int):
    event_rows = run_query(
        """
        SELECT
            event_id,
            user_id,
            event_date,
            start_time,
            end_time,
            description,
            workout_plan_id,
            workout_day_id
        FROM event
        WHERE event_id = :event_id
        AND user_id = :user_id
        AND event_type = 'workout'
        LIMIT 1
        """,
        {
            "event_id": event_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not event_rows:
        return {
            "success": False,
            "reason": "not_found",
            "message": "Workout event was not found.",
        }

    event = event_rows[0]

    if not event["workout_plan_id"] or not event["workout_day_id"]:
        return {
            "success": False,
            "reason": "invalid_event",
            "message": "This workout event is missing a workout plan or workout day.",
        }

    existing_event_session = run_query(
        """
        SELECT
            session_id,
            event_id,
            workout_plan_id,
            workout_day_id,
            started_at,
            ended_at,
            notes
        FROM workout_session
        WHERE user_id = :user_id
        AND event_id = :event_id
        LIMIT 1
        """,
        {
            "user_id": user_id,
            "event_id": event_id,
        },
        fetch=True,
        commit=False,
    )

    if existing_event_session:
        session_row = existing_event_session[0]

        return {
            "success": True,
            "message": "Session already exists for this event.",
            "session": {
                "sessionId": session_row["session_id"],
                "eventId": session_row["event_id"],
                "workoutPlanId": session_row["workout_plan_id"],
                "workoutDayId": session_row["workout_day_id"],
                "startedAt": _format_datetime(session_row["started_at"]),
                "endedAt": _format_datetime(session_row["ended_at"]),
                "notes": session_row["notes"],
            },
        }

    open_session = run_query(
        """
        SELECT
            session_id,
            event_id,
            workout_plan_id,
            workout_day_id,
            started_at,
            ended_at,
            notes
        FROM workout_session
        WHERE user_id = :user_id
        AND ended_at IS NULL
        ORDER BY started_at DESC
        LIMIT 1
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    if open_session:
        session_row = open_session[0]

        return {
            "success": True,
            "message": "You already have an active session.",
            "session": {
                "sessionId": session_row["session_id"],
                "eventId": session_row["event_id"],
                "workoutPlanId": session_row["workout_plan_id"],
                "workoutDayId": session_row["workout_day_id"],
                "startedAt": _format_datetime(session_row["started_at"]),
                "endedAt": _format_datetime(session_row["ended_at"]),
                "notes": session_row["notes"],
            },
        }

    session_id = run_query(
        """
        INSERT INTO workout_session (
            user_id,
            event_id,
            workout_plan_id,
            workout_day_id,
            started_at
        )
        VALUES (
            :user_id,
            :event_id,
            :workout_plan_id,
            :workout_day_id,
            NOW()
        )
        """,
        {
            "user_id": user_id,
            "event_id": event_id,
            "workout_plan_id": event["workout_plan_id"],
            "workout_day_id": event["workout_day_id"],
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    return {
        "success": True,
        "message": "Workout session started.",
        "session": {
            "sessionId": session_id,
            "eventId": event_id,
            "workoutPlanId": event["workout_plan_id"],
            "workoutDayId": event["workout_day_id"],
            "startedAt": None,
            "endedAt": None,
            "notes": None,
        },
    }


def get_session_exercises(user_id: int, session_id: int):
    session_rows = run_query(
        """
        SELECT
            session_id,
            workout_day_id
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

    if not session_rows:
        return {
            "success": False,
            "reason": "not_found",
            "message": "Session was not found.",
        }

    workout_day_id = session_rows[0]["workout_day_id"]

    if not workout_day_id:
        return {
            "success": False,
            "reason": "missing_workout_day",
            "message": "This session does not have a workout day.",
        }

    exercises = run_query(
        """
        SELECT
            e.exercise_id,
            e.exercise_name,
            e.equipment,
            e.video_url,
            e.description,
            pe.order_in_workout,
            pe.sets_goal,
            pe.reps_goal,
            pe.weight_goal
        FROM plan_exercise pe
        JOIN exercise e
            ON e.exercise_id = pe.exercise_id
        WHERE pe.day_id = :workout_day_id
        ORDER BY pe.order_in_workout ASC, e.exercise_name ASC
        """,
        {"workout_day_id": workout_day_id},
        fetch=True,
        commit=False,
    )

    mapped_exercises = []

    for exercise in exercises:
        mapped_exercises.append(
            {
                "exerciseId": exercise["exercise_id"],
                "exerciseName": exercise["exercise_name"],
                "equipment": exercise["equipment"],
                "videoUrl": exercise["video_url"],
                "description": exercise["description"],
                "orderInWorkout": exercise["order_in_workout"],
                "setsGoal": exercise["sets_goal"],
                "repsGoal": exercise["reps_goal"],
                "weightGoal": (
                    float(exercise["weight_goal"])
                    if exercise["weight_goal"] is not None
                    else None
                ),
            }
        )

    return {
        "success": True,
        "sessionId": session_id,
        "workoutDayId": workout_day_id,
        "exercises": mapped_exercises,
    }


def finish_session(user_id: int, session_id: int):
    session_rows = run_query(
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

    if not session_rows:
        return {
            "success": False,
            "reason": "not_found",
            "message": "Session was not found.",
        }

    if session_rows[0]["ended_at"] is not None:
        return {
            "success": True,
            "message": "Session was already finished.",
            "sessionId": session_id,
        }

    run_query(
        """
        UPDATE workout_session
        SET ended_at = NOW()
        WHERE session_id = :session_id
        AND user_id = :user_id
        AND ended_at IS NULL
        """,
        {
            "session_id": session_id,
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )

    return {
        "success": True,
        "message": "Workout session finished.",
        "sessionId": session_id,
    }


def get_due_workout_toast(user_id: int):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.description,
            e.start_time,
            e.end_time,
            ws.session_id,
            ws.ended_at
        FROM event e
        LEFT JOIN workout_session ws
            ON ws.event_id = e.event_id
            AND ws.user_id = e.user_id
        WHERE e.user_id = :user_id
        AND e.event_type = 'workout'
        AND e.event_date = CURDATE()
        AND e.start_time <= CURTIME()
        AND ws.session_id IS NULL
        ORDER BY e.start_time ASC
        LIMIT 1
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    workout = rows[0]

    return {
        "eventId": workout["event_id"],
        "title": "Workout ready",
        "body": f"{workout['description'] or 'Your workout'} is ready. Start it and finish today's workout.",
    }
