from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services.nutrition.mealLogging import getLoggedMeals


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _local_range_to_utc_strings(start_date, end_date, user_timezone: str | None):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    start_local = datetime.combine(start_date, time.min, tzinfo=tz)
    end_local = datetime.combine(end_date, time.max, tzinfo=tz)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

    return (
        start_utc.strftime("%Y-%m-%d %H:%M:%S"),
        end_utc.strftime("%Y-%m-%d %H:%M:%S"),
    )


def _to_local_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    return parsed_datetime.astimezone(ZoneInfo(_get_valid_timezone(user_timezone)))


def get_calories_metrics_service(user_id: int, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)
    now = datetime.now(ZoneInfo(valid_timezone))

    start_of_week = now - timedelta(days=now.weekday())
    start_of_week_date = start_of_week.date()
    end_of_week_date = start_of_week_date + timedelta(days=6)

    start_dt, end_dt = _local_range_to_utc_strings(
        start_date=start_of_week_date,
        end_date=end_of_week_date,
        user_timezone=valid_timezone,
    )

    meals = (
        getLoggedMeals(
            user_id=user_id,
            start_dt=start_dt,
            end_dt=end_dt,
        )
        or []
    )

    result_map = {}

    for i in range(7):
        day = start_of_week_date + timedelta(days=i)
        result_map[str(day)] = 0

    for meal in meals:
        if meal.get("calories") is None:
            continue

        eaten_at = meal.get("eaten_at")
        local_eaten_at = _to_local_datetime(eaten_at, valid_timezone)

        if local_eaten_at is None:
            continue

        day = local_eaten_at.date().isoformat()

        if day not in result_map:
            continue

        servings = float(meal.get("servings") or 0)
        calories = float(meal.get("calories") or 0)

        result_map[day] += calories * servings

    result = []

    for i in range(7):
        current_day = start_of_week_date + timedelta(days=i)

        result.append(
            {
                "day": current_day.strftime("%a"),
                "calories": round(result_map[str(current_day)]),
            }
        )

    return result
