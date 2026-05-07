from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services.nutrition.mealLogging import getLoggedMeals
from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _local_today_to_utc_range(user_timezone: str | None):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    today = datetime.now(tz).date()

    start_local = datetime.combine(today, time.min, tzinfo=tz)
    tomorrow_start_local = start_local + timedelta(days=1)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_start_utc = tomorrow_start_local.astimezone(timezone.utc).replace(
        tzinfo=None
    )

    return (
        start_utc.strftime("%Y-%m-%d %H:%M:%S"),
        tomorrow_start_utc.strftime("%Y-%m-%d %H:%M:%S"),
    )


def getNutrition(user_id, user_timezone: str | None = None):
    start_dt, end_dt = _local_today_to_utc_range(user_timezone)

    meals = getLoggedMeals(
        user_id=user_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    total = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
    }

    for meal in meals:
        servings = float(meal.get("servings") or 0)

        total["calories"] += float(meal.get("calories") or 0) * servings
        total["protein"] += float(meal.get("protein") or 0) * servings
        total["carbs"] += float(meal.get("carbs") or 0) * servings
        total["fat"] += float(meal.get("fats") or 0) * servings

    goals = run_query(
        """
        SELECT 
            calories_target,
            protein_target,
            carbs_target,
            fat_target
        FROM user_nutrition_goals
        WHERE user_id = :user_id
        """,
        {"user_id": user_id},
    )

    if goals:
        goal = goals[0]
        target = {
            "calories": goal.get("calories_target"),
            "protein": goal.get("protein_target"),
            "carbs": goal.get("carbs_target"),
            "fat": goal.get("fat_target"),
        }
    else:
        target = {
            "calories": None,
            "protein": None,
            "carbs": None,
            "fat": None,
        }

    return {
        "consumed": total,
        "target": target,
    }
