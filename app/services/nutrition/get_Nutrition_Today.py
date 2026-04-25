from datetime import datetime, time
from app.services.nutrition import mealLogging
from app.services.nutrition.getGoals import getNutritionGoals


def _format_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


def _get_meal_type(eaten_at):
    if isinstance(eaten_at, str):
        eaten_at = datetime.fromisoformat(eaten_at)

    hour = eaten_at.hour

    if hour < 11:
        return "Breakfast"
    if hour < 15:
        return "Lunch"
    if hour < 18:
        return "Snack"
    return "Dinner"


def _format_time_label(eaten_at):
    if isinstance(eaten_at, str):
        eaten_at = datetime.fromisoformat(eaten_at)

    return eaten_at.strftime("%I:%M %p").lstrip("0")


def get_nutrition_today(user_id: int):
    today = datetime.now().date()

    start_dt = datetime.combine(today, time.min).isoformat()
    end_dt = datetime.combine(today, time.max).isoformat()

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
                "meal_type": _get_meal_type(eaten_at),
                "eaten_at": _format_datetime(eaten_at),
                "time_label": _format_time_label(eaten_at),
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
