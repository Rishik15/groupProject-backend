from app.services import run_query


def get_meal_plan_library():
    """Returns all system meal plans (user_id = 1) ."""
    return run_query(
        """
        SELECT
            meal_plan_id,
            plan_name,
            total_calories
        FROM meal_plan
        WHERE user_id = 1
        ORDER BY plan_name ASC
        """,
        fetch=True, commit=False
    )