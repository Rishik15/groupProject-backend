from datetime import datetime, date, timedelta, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query
from app.services.nutrition.mealLogging import getLoggedMeals


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _local_day_to_utc_range(day_value: date, user_timezone: str | None):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    start_local = datetime.combine(day_value, time.min, tzinfo=tz)
    next_start_local = start_local + timedelta(days=1)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    next_start_utc = next_start_local.astimezone(timezone.utc).replace(tzinfo=None)

    return (
        start_utc.strftime("%Y-%m-%d %H:%M:%S"),
        next_start_utc.strftime("%Y-%m-%d %H:%M:%S"),
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


def userMetrics(user_id, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)
    today = datetime.now(ZoneInfo(valid_timezone)).date()

    today_start_utc, tomorrow_start_utc = _local_day_to_utc_range(
        day_value=today,
        user_timezone=valid_timezone,
    )

    meals = getLoggedMeals(
        user_id=user_id,
        start_dt=today_start_utc,
        end_dt=tomorrow_start_utc,
    )

    calories = 0

    for meal in meals:
        if meal.get("calories") is None:
            continue

        servings = float(meal.get("servings") or 0)
        calories += float(meal.get("calories") or 0) * servings

    steps = run_query(
        """
        SELECT COALESCE(SUM(steps), 0) AS total
        FROM cardio_log
        WHERE user_id = :user_id
        AND performed_at >= :today_start_utc
        AND performed_at < :tomorrow_start_utc
        """,
        {
            "user_id": user_id,
            "today_start_utc": today_start_utc,
            "tomorrow_start_utc": tomorrow_start_utc,
        },
    )[0]["total"]

    workouts = run_query(
        """
        SELECT COUNT(*) AS total
        FROM workout_session
        WHERE user_id = :user_id
        AND ended_at IS NOT NULL
        AND ended_at >= :today_start_utc
        AND ended_at < :tomorrow_start_utc
        """,
        {
            "user_id": user_id,
            "today_start_utc": today_start_utc,
            "tomorrow_start_utc": tomorrow_start_utc,
        },
    )[0]["total"]

    streak_rows = run_query(
        """
        SELECT ended_at
        FROM workout_session
        WHERE user_id = :user_id
        AND ended_at IS NOT NULL
        ORDER BY ended_at DESC
        """,
        {
            "user_id": user_id,
        },
    )

    workout_dates = set()

    for row in streak_rows:
        local_date = _utc_to_local_date(row["ended_at"], valid_timezone)

        if local_date is not None:
            workout_dates.add(local_date)

    streak = 0
    current_day = today

    while current_day in workout_dates:
        streak += 1
        current_day -= timedelta(days=1)

    return {
        "calories": int(calories),
        "steps": int(steps),
        "workouts": int(workouts),
        "streak": streak,
    }
