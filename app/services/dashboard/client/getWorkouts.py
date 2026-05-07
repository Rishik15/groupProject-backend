from datetime import date, datetime, time, timedelta, timezone
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


def _local_range_to_utc_strings(
    start_date: date, end_date: date, user_timezone: str | None
):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    start_local = datetime.combine(start_date, time.min, tzinfo=tz)
    end_local = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=tz)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

    return (
        start_utc.strftime("%Y-%m-%d %H:%M:%S"),
        end_utc.strftime("%Y-%m-%d %H:%M:%S"),
    )


def _utc_to_local_date(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    return parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    ).date()


def get_workout_completion_service(user_id: int, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)
    today = datetime.now(ZoneInfo(valid_timezone)).date()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    completed_start_utc, completed_end_utc = _local_range_to_utc_strings(
        start_date=start_of_week,
        end_date=end_of_week,
        user_timezone=valid_timezone,
    )

    planned_rows = run_query(
        """
        SELECT 
            event_date,
            COUNT(*) as planned_count
        FROM event
        WHERE user_id = :user_id
        AND event_type = 'workout'
        AND event_date BETWEEN :start AND :end
        GROUP BY event_date
        """,
        {
            "user_id": user_id,
            "start": start_of_week,
            "end": end_of_week,
        },
    )

    completed_rows = run_query(
        """
        SELECT 
            ended_at
        FROM workout_session
        WHERE user_id = :user_id
        AND ended_at IS NOT NULL
        AND ended_at >= :start_utc
        AND ended_at < :end_utc
        """,
        {
            "user_id": user_id,
            "start_utc": completed_start_utc,
            "end_utc": completed_end_utc,
        },
    )

    planned_map = {row["event_date"]: row["planned_count"] for row in planned_rows}

    completed_map = {}

    for row in completed_rows:
        local_day = _utc_to_local_date(row["ended_at"], valid_timezone)

        if local_day is None:
            continue

        completed_map[local_day] = completed_map.get(local_day, 0) + 1

    days = []
    total_planned = 0
    total_completed = 0

    for i in range(7):
        current_day = start_of_week + timedelta(days=i)

        planned = int(planned_map.get(current_day, 0))
        completed = int(completed_map.get(current_day, 0))

        total_planned += planned
        total_completed += completed

        days.append(
            {
                "day": current_day.strftime("%a"),
                "date": str(current_day),
                "planned": planned,
                "completed": completed,
            }
        )

    return {
        "days": days,
        "summary": {
            "planned": total_planned,
            "completed": total_completed,
        },
    }
