from app.services import run_query


def get_my_meal_plans(user_id, today):
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
          AND (
              end_date IS NULL
              OR end_date >= :today
          )
        ORDER BY
            CASE
                WHEN start_date IS NULL THEN 1
                ELSE 0
            END,
            start_date ASC,
            created_at DESC
        """,
        {
            "user_id": user_id,
            "today": today,
        },
        fetch=True,
        commit=False,
    )
