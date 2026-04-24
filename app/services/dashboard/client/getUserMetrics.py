from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from app.services import run_query
from app.services.nutrition.mealLogging import getLoggedMeals

NY_TZ = ZoneInfo("America/New_York")


def userMetrics(user_id):
    now = datetime.now(NY_TZ)

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    meals = getLoggedMeals(
        user_id=user_id,
        start_dt=start.isoformat(),
        end_dt=end.isoformat(),
    )

    calories = 0
    for meal in meals:
        if meal.get("calories") is None:
            continue

        servings = float(meal.get("servings") or 0)
        calories += float(meal.get("calories") or 0) * servings

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
