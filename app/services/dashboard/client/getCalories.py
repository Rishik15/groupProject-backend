from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.services.nutrition.mealLogging import getLoggedMeals


def get_calories_metrics_service(user_id: int):
    now = datetime.now()

    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    end_of_week = start_of_week + timedelta(days=6)
    end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)

    meals = getLoggedMeals(
        user_id=user_id,
        start_dt=start_of_week.isoformat(),
        end_dt=end_of_week.isoformat(),
    )

    result_map = {}
    for i in range(7):
        day = (start_of_week + timedelta(days=i)).date()
        result_map[str(day)] = 0

    for meal in meals:
        if meal.get("calories") is None:
            continue

        eaten_at = meal.get("eaten_at")
        if not eaten_at:
            continue

        day = eaten_at.split("T")[0]

        servings = float(meal.get("servings") or 0)
        calories = float(meal.get("calories") or 0)

        result_map[day] += calories * servings

    result = []
    for i in range(7):
        current_day = (start_of_week + timedelta(days=i)).date()

        result.append(
            {
                "day": current_day.strftime("%a"),
                "calories": result_map[str(current_day)],
            }
        )

    return result
