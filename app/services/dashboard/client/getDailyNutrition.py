from datetime import datetime
from zoneinfo import ZoneInfo
from app.services.nutrition.mealLogging import getLoggedMeals
from app.services import run_query

NY_TZ = ZoneInfo("America/New_York")


def getNutrition(user_id):

    now = datetime.now(NY_TZ)

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    meals = getLoggedMeals(
        user_id=user_id, start_dt=start.isoformat(), end_dt=end.isoformat()
    )

    total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

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
        g = goals[0]
        target = {
            "calories": g.get("calories_target"),
            "protein": g.get("protein_target"),
            "carbs": g.get("carbs_target"),
            "fat": g.get("fat_target"),
        }
    else:
        target = {"calories": None, "protein": None, "carbs": None, "fat": None}

    return {"consumed": total, "target": target}
