from app.services import run_query


def get_my_meal_plans(user_id):
    return run_query(
        """
        SELECT
            meal_plan_id,
            plan_name,
            DATE_FORMAT(start_date, '%Y-%m-%d') AS start_date,
            DATE_FORMAT(end_date, '%Y-%m-%d') AS end_date,
            total_calories
        FROM meal_plan
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        """,
        {"user_id": user_id},
        fetch=True, commit=False
    )