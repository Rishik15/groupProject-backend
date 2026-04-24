from app.services import run_query


def getNutritionGoals(user_id: int):
    result = run_query(
        """
        SELECT
            calories_target,
            protein_target,
            carbs_target,
            fat_target
        FROM user_nutrition_goals
        WHERE user_id = :uid
        LIMIT 1
        """,
        {"uid": user_id},
        fetch=True,
        commit=False,
    )

    if not result:
        return None

    return result[0]
