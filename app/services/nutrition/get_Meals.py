from app.services import run_query


def get_meals():
    return run_query(
        """
        SELECT
            meal_id,
            name,
            calories,
            protein,
            carbs,
            fats
        FROM meal
        ORDER BY name ASC
        """,
        fetch=True, commit=False
    )