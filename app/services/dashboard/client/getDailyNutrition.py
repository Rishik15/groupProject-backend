from app.services import run_query


def getNutrition(user_id):

    result = run_query(
        """
        SELECT 
            SUM(
                CASE 
                    WHEN ml.meal_id IS NOT NULL THEN m.protein * ml.servings
                    ELSE fi.protein * ml.servings
                END
            ) AS protein,

            SUM(
                CASE 
                    WHEN ml.meal_id IS NOT NULL THEN m.carbs * ml.servings
                    ELSE fi.carbs * ml.servings
                END
            ) AS carbs,

            SUM(
                CASE 
                    WHEN ml.meal_id IS NOT NULL THEN m.fats * ml.servings
                    ELSE fi.fats * ml.servings
                END
            ) AS fat,

            SUM(
                CASE 
                    WHEN ml.meal_id IS NOT NULL THEN m.calories * ml.servings
                    ELSE fi.calories * ml.servings
                END
            ) AS calories

        FROM meal_log ml
        LEFT JOIN meal m ON ml.meal_id = m.meal_id
        LEFT JOIN food_item fi ON ml.food_item_id = fi.food_item_id

        WHERE ml.user_id = :user_id
        AND DATE(ml.eaten_at) = CURDATE()
        """,
        {"user_id": user_id},
    )

    totals = result[0] if result else {}

    consumed = {
        "calories": totals.get("calories") or 0,
        "protein": totals.get("protein") or 0,
        "carbs": totals.get("carbs") or 0,
        "fat": totals.get("fat") or 0,
    }

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
            "calories": g["calories_target"],
            "protein": g["protein_target"],
            "carbs": g["carbs_target"],
            "fat": g["fat_target"],
        }
    else:
        target = {"calories": None, "protein": None, "carbs": None, "fat": None}

    return {"consumed": consumed, "target": target}
