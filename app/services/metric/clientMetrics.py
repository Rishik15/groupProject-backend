from app.services import run_query
from datetime import datetime, timedelta


def clientMetrics(user_id: int):
    calories_query = """
    SELECT 
      SUM(
        CASE 
          WHEN ml.meal_id IS NOT NULL THEN m.calories * ml.servings
          WHEN ml.food_item_id IS NOT NULL THEN fi.calories * ml.servings
          ELSE 0
        END
      ) AS total_calories
    FROM meal_log ml
    LEFT JOIN meal m ON ml.meal_id = m.meal_id
    LEFT JOIN food_item fi ON ml.food_item_id = fi.food_item_id
    WHERE ml.user_id = :user_id
      AND DATE(ml.eaten_at) = CURDATE();
    """

    calories_result = run_query(calories_query, {"user_id": user_id})
    calories = calories_result[0]["total_calories"] or 0

    steps_query = """
    SELECT SUM(steps) AS total_steps
    FROM cardio_log
    WHERE user_id = :user_id
      AND DATE(performed_at) = CURDATE();
    """

    steps_result = run_query(steps_query, {"user_id": user_id})
    steps = steps_result[0]["total_steps"] or 0

    workouts_query = """
    SELECT COUNT(*) AS workouts_today
    FROM workout_session
    WHERE user_id = :user_id
      AND DATE(started_at) = CURDATE();
    """

    workouts_result = run_query(workouts_query, {"user_id": user_id})
    workouts = workouts_result[0]["workouts_today"] or 0

    streak_query = """
    SELECT DISTINCT DATE(started_at) AS workout_date
    FROM workout_session
    WHERE user_id = :user_id
    ORDER BY workout_date DESC;
    """

    streak_result = run_query(streak_query, {"user_id": user_id})

    dates = [row["workout_date"] for row in streak_result]

    streak = 0
    today = datetime.utcnow().date()

    current = today

    for d in dates:
        diff = (current - d).days

        if diff == 0 or diff == 1:
            streak += 1
            current = d
        else:
            break

    return {
        "calories": calories,
        "steps": steps,
        "workouts": workouts,
        "streak": streak,
    }
