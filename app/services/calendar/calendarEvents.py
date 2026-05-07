from datetime import date, datetime, time, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _date_to_string(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return str(value)


def _timedelta_to_time(value: timedelta):
    total_seconds = int(value.total_seconds())

    if total_seconds < 0:
        total_seconds = 0

    total_seconds = total_seconds % 86400

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return time(hour=hours, minute=minutes, second=seconds)


def _coerce_time(value):
    if value is None:
        return None

    if isinstance(value, time):
        return value

    if isinstance(value, datetime):
        return value.time()

    if isinstance(value, timedelta):
        return _timedelta_to_time(value)

    if isinstance(value, str):
        cleaned_value = value.strip()

        try:
            return datetime.strptime(cleaned_value, "%H:%M:%S").time()
        except ValueError:
            try:
                return datetime.strptime(cleaned_value, "%H:%M").time()
            except ValueError:
                return None

    return None


def _time_to_string(value):
    coerced_time = _coerce_time(value)

    if coerced_time is None:
        return None

    return coerced_time.strftime("%H:%M:%S")


def _format_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        try:
            parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))
        except (ValueError, TypeError):
            return str(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    local_datetime = parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    )

    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def _get_event_local_datetime(row, user_timezone: str | None):
    event_date = row.get("event_date")
    end_time = _coerce_time(row.get("end_time"))

    if event_date is None or end_time is None:
        return None

    if isinstance(event_date, datetime):
        event_date = event_date.date()

    if isinstance(event_date, str):
        try:
            event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            return None

    if not isinstance(event_date, date):
        return None

    tz = ZoneInfo(_get_valid_timezone(user_timezone))

    return datetime.combine(event_date, end_time, tzinfo=tz)


def _get_workout_status(row, user_timezone: str | None):
    if row.get("event_type") != "workout":
        return None

    session_id = row.get("session_id")
    ended_at = row.get("session_ended_at")
    event_local_datetime = _get_event_local_datetime(row, user_timezone)

    if session_id and ended_at is not None:
        return "completed"

    if session_id and ended_at is None:
        return "active"

    if event_local_datetime and event_local_datetime < datetime.now(
        ZoneInfo(_get_valid_timezone(user_timezone))
    ):
        return "missed"

    return "scheduled"


def _serialize_event(row, user_timezone: str | None = None):
    if not row:
        return None

    if row.get("event_date") is None:
        return None

    if row.get("start_time") is None or row.get("end_time") is None:
        return None

    event_type = row.get("event_type")
    description = row.get("description") or ""
    notes = row.get("notes") or ""
    workout_plan_name = row.get("workout_plan_name")
    workout_day_label = row.get("workout_day_label")
    workout_status = _get_workout_status(row, user_timezone)

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
        "sessionId": row.get("session_id"),
        "sessionStartedAt": _format_datetime(
            row.get("session_started_at"),
            user_timezone,
        ),
        "sessionEndedAt": _format_datetime(
            row.get("session_ended_at"),
            user_timezone,
        ),
        "workoutStatus": workout_status,
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


def get_events_for_user_range(
    user_id: int,
    start_date: date,
    end_date: date,
    user_timezone: str | None = None,
):
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
            wd.day_order AS workout_day_order,
            ws.session_id,
            ws.started_at AS session_started_at,
            ws.ended_at AS session_ended_at
        FROM event e
        LEFT JOIN workout_plan wp
            ON wp.plan_id = e.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = e.workout_day_id
        LEFT JOIN workout_session ws
            ON ws.event_id = e.event_id
            AND ws.user_id = e.user_id
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

    events = []

    for row in rows:
        event = _serialize_event(row, user_timezone)

        if event is not None:
            events.append(event)

    return events


def get_event_by_id_for_user(
    user_id: int,
    event_id: int,
    user_timezone: str | None = None,
):
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
            wd.day_order AS workout_day_order,
            ws.session_id,
            ws.started_at AS session_started_at,
            ws.ended_at AS session_ended_at
        FROM event e
        LEFT JOIN workout_plan wp
            ON wp.plan_id = e.workout_plan_id
        LEFT JOIN workout_day wd
            ON wd.day_id = e.workout_day_id
        LEFT JOIN workout_session ws
            ON ws.event_id = e.event_id
            AND ws.user_id = e.user_id
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

    return _serialize_event(rows[0], user_timezone) if rows else None


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
    user_timezone: str | None = None,
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

    return get_event_by_id_for_user(user_id, event_id, user_timezone)


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
    user_timezone: str | None = None,
):
    existing = get_event_by_id_for_user(user_id, event_id, user_timezone)

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

    return get_event_by_id_for_user(user_id, event_id, user_timezone)


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
