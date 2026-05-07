from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services.nutrition import mealLogging
from app.services.nutrition.getGoals import getNutritionGoals


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _get_today_utc_range(user_timezone: str | None):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    today = datetime.now(tz).date()

    start_local = datetime.combine(today, time.min, tzinfo=tz)
    end_local = datetime.combine(today, time.max, tzinfo=tz)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

    return (
        start_utc.strftime("%Y-%m-%d %H:%M:%S"),
        end_utc.strftime("%Y-%m-%d %H:%M:%S"),
    )


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


def _get_meal_type(eaten_at, user_timezone: str | None):
    local_eaten_at = _to_local_datetime(eaten_at, user_timezone)

    if local_eaten_at is None:
        return "Meal"

    hour = local_eaten_at.hour

    if hour < 11:
        return "Breakfast"

    if hour < 15:
        return "Lunch"

    if hour < 18:
        return "Snack"

    return "Dinner"


def _format_time_label(eaten_at, user_timezone: str | None):
    local_eaten_at = _to_local_datetime(eaten_at, user_timezone)

    if local_eaten_at is None:
        return ""

    return local_eaten_at.strftime("%I:%M %p").lstrip("0")


def get_nutrition_today(user_id: int, user_timezone: str | None = None):
    start_dt, end_dt = _get_today_utc_range(user_timezone)

    meals = (
        mealLogging.getLoggedMeals(
            user_id=user_id,
            start_dt=start_dt,
            end_dt=end_dt,
        )
        or []
    )

    goals = getNutritionGoals(user_id)

    if goals:
        calorie_goal = goals.get("calories_target")
        protein_goal = goals.get("protein_target")
        carbs_goal = goals.get("carbs_target")
        fats_goal = goals.get("fat_target")
    else:
        calorie_goal = None
        protein_goal = None
        carbs_goal = None
        fats_goal = None

    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

    formatted_meals = []

    for meal in meals:
        servings = float(meal.get("servings") or 1)

        calories = float(meal.get("calories") or 0) * servings
        protein = float(meal.get("protein") or 0) * servings
        carbs = float(meal.get("carbs") or 0) * servings
        fats = float(meal.get("fats") or 0) * servings

        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fats += fats

        eaten_at = meal.get("eaten_at")

        formatted_meals.append(
            {
                "log_id": meal.get("log_id"),
                "meal_name": meal.get("meal_name") or "Meal",
                "meal_type": (
                    "Food"
                    if meal.get("meal_id") is None
                    else _get_meal_type(eaten_at, user_timezone)
                ),
                "eaten_at": _format_datetime(eaten_at, user_timezone),
                "time_label": _format_time_label(eaten_at, user_timezone),
                "servings": servings,
                "notes": meal.get("notes"),
                "photo_url": meal.get("photo_url"),
                "calories": round(calories),
                "protein": round(protein, 1),
                "carbs": round(carbs, 1),
                "fats": round(fats, 1),
            }
        )

    return {
        "message": "success",
        "calories": {
            "current": round(total_calories),
            "goal": calorie_goal,
        },
        "macros": {
            "protein": {
                "current": round(total_protein, 1),
                "goal": protein_goal,
            },
            "carbs": {
                "current": round(total_carbs, 1),
                "goal": carbs_goal,
            },
            "fats": {
                "current": round(total_fats, 1),
                "goal": fats_goal,
            },
        },
        "meals": formatted_meals,
    }
