from app.services import run_query
from datetime import date, timedelta


def userMetrics(user_id):
    calories = run_query(
        """
        SELECT 
            COALESCE(SUM(
                COALESCE(m.calories, f.calories) * ml.servings
            ), 0) AS total
        FROM meal_log ml
        LEFT JOIN meal m ON ml.meal_id = m.meal_id
        LEFT JOIN food_item f ON ml.food_item_id = f.food_item_id
        WHERE ml.user_id = :user_id
        AND DATE(ml.eaten_at) = CURDATE()
    """,
        {"user_id": user_id},
    )[0]["total"]

    steps = run_query(
        """
        SELECT COALESCE(SUM(steps), 0) AS total
        FROM cardio_log
        WHERE user_id = :user_id
        AND DATE(performed_at) = CURDATE()
    """,
        {"user_id": user_id},
    )[0]["total"]

    workouts = run_query(
        """
    SELECT COUNT(*) AS total
    FROM workout_session
    WHERE user_id = :user_id
    AND ended_at IS NOT NULL
    AND DATE(ended_at) = CURDATE()
""",
        {"user_id": user_id},
    )[0]["total"]

    streak_rows = run_query(
        """
    SELECT DATE(ended_at) as workout_date
    FROM workout_session
    WHERE user_id = :user_id
    AND ended_at IS NOT NULL
    GROUP BY DATE(ended_at)
    ORDER BY workout_date DESC
    """,
        {"user_id": user_id},
    )

    streak = 0
    current_day = date.today()

    workout_dates = set(row["workout_date"] for row in streak_rows)

    while current_day in workout_dates:
        streak += 1
        current_day -= timedelta(days=1)

    return {
        "calories": int(calories),
        "steps": int(steps),
        "workouts": int(workouts),
        "streak": streak,
    }
