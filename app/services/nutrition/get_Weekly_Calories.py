from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services.nutrition import mealLogging
from app.services.nutrition.getGoals import getNutritionGoals

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def get_week_monday(date_value: datetime):
    return date_value - timedelta(days=date_value.weekday())


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


def get_weekly_calories(user_id: int, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)
    now = datetime.now(ZoneInfo(valid_timezone))

    monday = get_week_monday(now).date()
    sunday = monday + timedelta(days=6)

    start_dt, end_dt = _local_range_to_utc_strings(
        start_date=monday,
        end_date=sunday,
        user_timezone=valid_timezone,
    )

    meals = (
        mealLogging.getLoggedMeals(
            user_id=user_id,
            start_dt=start_dt,
            end_dt=end_dt,
        )
        or []
    )

    daily_totals = {}

    for meal in meals:
        eaten_at = meal.get("eaten_at")
        local_eaten_at = _to_local_datetime(eaten_at, valid_timezone)

        if local_eaten_at is None:
            continue

        date_key = local_eaten_at.date().strftime("%Y-%m-%d")
        calories = float(meal.get("calories") or 0)
        servings = float(meal.get("servings") or 1)

        daily_totals[date_key] = daily_totals.get(date_key, 0) + calories * servings

    days = []

    for index, label in enumerate(DAY_LABELS):
        current_date = monday + timedelta(days=index)
        day_key = current_date.strftime("%Y-%m-%d")

        days.append(
            {
                "dayKey": day_key,
                "dayLabel": label,
                "calories": round(daily_totals.get(day_key, 0)),
            }
        )

    total_calories = sum(day["calories"] for day in days)
    average_daily_calories = round(total_calories / 7)

    best_day_calories = max((day["calories"] for day in days), default=0)

    goals = getNutritionGoals(user_id)
    goal_calories = goals.get("calories_target") if goals else None

    return {
        "message": "success",
        "days": days,
        "averageDailyCalories": average_daily_calories,
        "bestDayCalories": best_day_calories,
        "goalCalories": goal_calories,
    }
