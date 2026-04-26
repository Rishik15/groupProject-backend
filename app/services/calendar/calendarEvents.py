from datetime import date, datetime, time
from app.services import run_query


def _date_to_string(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return str(value)


def _time_to_string(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")

    if isinstance(value, time):
        return value.strftime("%H:%M:%S")

    return str(value)


def _serialize_event(row):
    if not row:
        return None

    event_type = row.get("event_type")
    description = row.get("description") or ""
    notes = row.get("notes") or ""
    workout_plan_name = row.get("workout_plan_name")
    workout_day_label = row.get("workout_day_label")

    title = description

    if not title:
        if event_type == "coach_session":
            title = "Coach Session"
        elif workout_day_label:
            title = workout_day_label
        elif workout_plan_name:
            title = workout_plan_name
        else:
            title = "Workout Session"

    return {
        "id": str(row["event_id"]),
        "eventId": int(row["event_id"]),
        "userId": int(row["user_id"]),
        "title": title,
        "date": _date_to_string(row.get("event_date")),
        "startTime": _time_to_string(row.get("start_time")),
        "endTime": _time_to_string(row.get("end_time")),
        "eventType": event_type,
        "description": description,
        "notes": notes,
        "workoutPlanId": row.get("workout_plan_id"),
        "workoutPlanName": workout_plan_name,
        "workoutDayId": row.get("workout_day_id"),
        "workoutDayLabel": workout_day_label,
        "workoutDayOrder": row.get("workout_day_order"),
    }


def workout_plan_exists(workout_plan_id: int):
    rows = run_query(
        """
        SELECT plan_id
        FROM workout_plan
        WHERE plan_id = :plan_id
        LIMIT 1
        """,
        {"plan_id": workout_plan_id},
        fetch=True,
        commit=False,
    )

    return len(rows) > 0


def workout_day_belongs_to_plan(workout_plan_id: int, workout_day_id: int):
    rows = run_query(
        """
        SELECT day_id
        FROM workout_day
        WHERE plan_id = :plan_id
        AND day_id = :day_id
        LIMIT 1
        """,
        {
            "plan_id": workout_plan_id,
            "day_id": workout_day_id,
        },
        fetch=True,
        commit=False,
    )

    return len(rows) > 0


def get_events_for_user_range(user_id: int, start_date: date, end_date: date):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.user_id,
            e.event_date,
            e.start_time,
            e.end_time,
            e.event_type,
            e.description,
            e.notes,
            e.workout_plan_id,
            e.workout_day_id,
            wp.plan_name AS workout_plan_name,
            wd.day_label AS workout_day_label,
            wd.day_order AS workout_day_order
        FROM event e
        LEFT JOIN workout_plan wp
            ON wp.plan_id = e.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = e.workout_day_id
        WHERE e.user_id = :user_id
        AND e.event_date BETWEEN :start_date AND :end_date
        ORDER BY e.event_date ASC, e.start_time ASC, e.event_id ASC
        """,
        {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        fetch=True,
        commit=False,
    )

    return [_serialize_event(row) for row in rows]


def get_event_by_id_for_user(user_id: int, event_id: int):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.user_id,
            e.event_date,
            e.start_time,
            e.end_time,
            e.event_type,
            e.description,
            e.notes,
            e.workout_plan_id,
            e.workout_day_id,
            wp.plan_name AS workout_plan_name,
            wd.day_label AS workout_day_label,
            wd.day_order AS workout_day_order
        FROM event e
        LEFT JOIN workout_plan wp
            ON wp.plan_id = e.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = e.workout_day_id
        WHERE e.user_id = :user_id
        AND e.event_id = :event_id
        LIMIT 1
        """,
        {
            "user_id": user_id,
            "event_id": event_id,
        },
        fetch=True,
        commit=False,
    )

    return _serialize_event(rows[0]) if rows else None


def create_event(
    user_id: int,
    event_date: date,
    start_time: time,
    end_time: time,
    event_type: str,
    description: str | None = None,
    notes: str | None = None,
    workout_plan_id: int | None = None,
    workout_day_id: int | None = None,
):
    event_id = run_query(
        """
        INSERT INTO event
            (
                user_id,
                event_date,
                start_time,
                end_time,
                event_type,
                description,
                notes,
                workout_plan_id,
                workout_day_id
            )
        VALUES
            (
                :user_id,
                :event_date,
                :start_time,
                :end_time,
                :event_type,
                :description,
                :notes,
                :workout_plan_id,
                :workout_day_id
            )
        """,
        {
            "user_id": user_id,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "event_type": event_type,
            "description": description or "",
            "notes": notes or "",
            "workout_plan_id": workout_plan_id,
            "workout_day_id": workout_day_id,
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    return get_event_by_id_for_user(user_id, event_id)


def update_event(
    user_id: int,
    event_id: int,
    event_date: date | None = None,
    start_time: time | None = None,
    end_time: time | None = None,
    description: str | None = None,
    notes: str | None = None,
    workout_plan_id: int | None = None,
    workout_day_id: int | None = None,
    clear_workout_fields: bool = False,
):
    existing = get_event_by_id_for_user(user_id, event_id)

    if not existing:
        return None

    next_event_date = event_date if event_date is not None else existing["date"]
    next_start_time = start_time if start_time is not None else existing["startTime"]
    next_end_time = end_time if end_time is not None else existing["endTime"]
    next_description = (
        description if description is not None else existing["description"]
    )
    next_notes = notes if notes is not None else existing["notes"]

    if clear_workout_fields:
        next_workout_plan_id = None
        next_workout_day_id = None
    else:
        next_workout_plan_id = (
            workout_plan_id
            if workout_plan_id is not None
            else existing["workoutPlanId"]
        )

        next_workout_day_id = (
            workout_day_id if workout_day_id is not None else existing["workoutDayId"]
        )

    run_query(
        """
        UPDATE event
        SET
            event_date = :event_date,
            start_time = :start_time,
            end_time = :end_time,
            description = :description,
            notes = :notes,
            workout_plan_id = :workout_plan_id,
            workout_day_id = :workout_day_id
        WHERE user_id = :user_id
        AND event_id = :event_id
        """,
        {
            "event_date": next_event_date,
            "start_time": next_start_time,
            "end_time": next_end_time,
            "description": next_description or "",
            "notes": next_notes or "",
            "workout_plan_id": next_workout_plan_id,
            "workout_day_id": next_workout_day_id,
            "user_id": user_id,
            "event_id": event_id,
        },
        fetch=False,
        commit=True,
    )

    return get_event_by_id_for_user(user_id, event_id)


def delete_event(user_id: int, event_id: int):
    existing = get_event_by_id_for_user(user_id, event_id)

    if not existing:
        return False

    run_query(
        """
        DELETE FROM event
        WHERE user_id = :user_id
        AND event_id = :event_id
        """,
        {
            "user_id": user_id,
            "event_id": event_id,
        },
        fetch=False,
        commit=True,
    )

    return True
