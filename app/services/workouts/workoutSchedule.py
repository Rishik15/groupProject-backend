import json
from datetime import date, datetime, time

from app.services import run_query


ALLOWED_SESSION_TYPES = {
    "strength",
    "cardio",
    "yoga",
    "rest",
    "nutrition",
    "other",
}

ALLOWED_STATUSES = {
    "scheduled",
    "active",
    "done",
    "missed",
}


def _normalize_session_type(value):
    if value in ALLOWED_SESSION_TYPES:
        return value
    return "strength"


def _normalize_status(value):
    if value == "complete":
        return "done"

    if value in ALLOWED_STATUSES:
        return value

    return "scheduled"


def _parse_metadata(description):
    if not description:
        return {}

    try:
        parsed = json.loads(description)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    return {"notes": description}


def _build_metadata(
    title,
    session_type,
    status,
    notes=None,
    session_id=None,
):
    payload = {
        "title": title,
        "session_type": _normalize_session_type(session_type),
        "status": _normalize_status(status),
        "notes": notes or "",
        "session_id": session_id,
    }

    return json.dumps(payload)


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


def _serialize_event_row(row):
    metadata = _parse_metadata(row.get("description"))

    raw_title = metadata.get("title")
    title = (
        raw_title.strip()
        if isinstance(raw_title, str) and raw_title.strip()
        else "Workout Session"
    )

    raw_notes = metadata.get("notes")
    notes = raw_notes.strip() if isinstance(raw_notes, str) else ""

    raw_session_id = metadata.get("session_id")
    session_id = raw_session_id if isinstance(raw_session_id, int) else None

    return {
        "event_id": int(row["event_id"]),
        "title": title,
        "event_date": _date_to_string(row.get("event_date")),
        "start_time": _time_to_string(row.get("start_time")),
        "end_time": _time_to_string(row.get("end_time")),
        "session_type": _normalize_session_type(metadata.get("session_type")),
        "status": _normalize_status(metadata.get("status")),
        "notes": notes,
        "workout_plan_id": row.get("workout_plan_id"),
        "session_id": session_id,
    }


def _get_raw_event_row(user_id, event_id):
    rows = run_query(
        """
        SELECT
            event_id,
            user_id,
            event_date,
            start_time,
            end_time,
            event_type,
            description,
            workout_plan_id
        FROM event
        WHERE user_id = :uid
          AND event_id = :eid
          AND event_type = 'workout'
        LIMIT 1;
        """,
        {
            "uid": user_id,
            "eid": event_id,
        },
    )

    return rows[0] if rows else None


def getWorkoutScheduleEventById(user_id: int, event_id: int):
    row = _get_raw_event_row(user_id, event_id)
    if not row:
        return None

    return _serialize_event_row(row)


def getWorkoutScheduleEventsForRange(user_id: int, start_date: date, end_date: date):
    rows = run_query(
        """
        SELECT
            event_id,
            user_id,
            event_date,
            start_time,
            end_time,
            event_type,
            description,
            workout_plan_id
        FROM event
        WHERE user_id = :uid
          AND event_type = 'workout'
          AND event_date BETWEEN :start_date AND :end_date
        ORDER BY event_date ASC, start_time ASC, event_id ASC;
        """,
        {
            "uid": user_id,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return [_serialize_event_row(row) for row in rows]


def createWorkoutScheduleEvent(
    user_id: int,
    title: str,
    event_date: date,
    start_time: time,
    end_time: time,
    session_type: str,
    status: str,
    notes: str | None = None,
    workout_plan_id: int | None = None,
):
    description = _build_metadata(
        title=title,
        session_type=session_type,
        status=status,
        notes=notes,
    )

    run_query(
        """
        INSERT INTO event
            (
                user_id,
                event_date,
                start_time,
                end_time,
                event_type,
                description,
                workout_plan_id
            )
        VALUES
            (
                :uid,
                :event_date,
                :start_time,
                :end_time,
                'workout',
                :description,
                :workout_plan_id
            );
        """,
        {
            "uid": user_id,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "workout_plan_id": workout_plan_id,
        },
        fetch=False,
        commit=True,
    )

    rows = run_query(
        """
        SELECT
            event_id,
            user_id,
            event_date,
            start_time,
            end_time,
            event_type,
            description,
            workout_plan_id
        FROM event
        WHERE user_id = :uid
          AND event_type = 'workout'
          AND event_date = :event_date
          AND start_time = :start_time
          AND end_time = :end_time
        ORDER BY event_id DESC
        LIMIT 1;
        """,
        {
            "uid": user_id,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
        },
    )

    return _serialize_event_row(rows[0]) if rows else None


def updateWorkoutScheduleEvent(
    user_id: int,
    event_id: int,
    title: str | None = None,
    event_date: date | None = None,
    start_time: time | None = None,
    end_time: time | None = None,
    session_type: str | None = None,
    status: str | None = None,
    notes: str | None = None,
    workout_plan_id: int | None = None,
):
    current = _get_raw_event_row(user_id, event_id)
    if not current:
        return None

    current_meta = _parse_metadata(current.get("description"))

    next_title = title
    if next_title is None:
        next_title = current_meta.get("title") or "Workout Session"

    next_session_type = _normalize_session_type(
        session_type if session_type is not None else current_meta.get("session_type")
    )

    next_status = _normalize_status(
        status if status is not None else current_meta.get("status")
    )

    next_notes = notes if notes is not None else current_meta.get("notes") or ""

    raw_session_id = current_meta.get("session_id")
    next_session_id = raw_session_id if isinstance(raw_session_id, int) else None

    next_description = _build_metadata(
        title=next_title,
        session_type=next_session_type,
        status=next_status,
        notes=next_notes,
        session_id=next_session_id,
    )

    run_query(
        """
        UPDATE event
        SET event_date = :event_date,
            start_time = :start_time,
            end_time = :end_time,
            description = :description,
            workout_plan_id = :workout_plan_id
        WHERE user_id = :uid
          AND event_id = :eid
          AND event_type = 'workout';
        """,
        {
            "event_date": event_date if event_date is not None else current.get("event_date"),
            "start_time": start_time if start_time is not None else current.get("start_time"),
            "end_time": end_time if end_time is not None else current.get("end_time"),
            "description": next_description,
            "workout_plan_id": (
                workout_plan_id
                if workout_plan_id is not None
                else current.get("workout_plan_id")
            ),
            "uid": user_id,
            "eid": event_id,
        },
        fetch=False,
        commit=True,
    )

    return getWorkoutScheduleEventById(user_id, event_id)


def deleteWorkoutScheduleEvent(user_id: int, event_id: int):
    existing = getWorkoutScheduleEventById(user_id, event_id)
    if not existing:
        return False

    run_query(
        """
        DELETE FROM event
        WHERE user_id = :uid
          AND event_id = :eid
          AND event_type = 'workout';
        """,
        {
            "uid": user_id,
            "eid": event_id,
        },
        fetch=False,
        commit=True,
    )

    return True