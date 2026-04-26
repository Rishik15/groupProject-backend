from datetime import datetime, timedelta, time
from app.services.nutrition import mealLogging
from app.services.nutrition.getGoals import getNutritionGoals

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_week_monday(date: datetime):
    return date - timedelta(days=date.weekday())


def get_weekly_calories(user_id: int):
    now = datetime.now()
    monday = get_week_monday(now).date()
    sunday = monday + timedelta(days=6)

    start_dt = datetime.combine(monday, time.min).isoformat()
    end_dt = datetime.combine(sunday, time.max).isoformat()

    meals = mealLogging.getLoggedMeals(
        user_id=user_id,
        start_dt=start_dt,
        end_dt=end_dt,
    ) or []

    daily_totals = {}

    for meal in meals:
        eaten_at = meal.get("eaten_at")

        if isinstance(eaten_at, str):
            eaten_date = datetime.fromisoformat(eaten_at).date()
        else:
            eaten_date = eaten_at.date()

        date_key = eaten_date.strftime("%Y-%m-%d")
        calories = float(meal.get("calories") or 0)
        servings = float(meal.get("servings") or 1)

        daily_totals[date_key] = daily_totals.get(date_key, 0) + calories * servings

    days = []

    for index, label in enumerate(DAY_LABELS):
        current_date = monday + timedelta(days=index)
        day_key = current_date.strftime("%Y-%m-%d")

        days.append({
            "dayKey": day_key,
            "dayLabel": label,
            "calories": round(daily_totals.get(day_key, 0)),
        })

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