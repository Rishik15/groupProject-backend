from app.services import run_query
from datetime import datetime, timedelta


def get_calories_metrics_service(user_id: int):
    rows = run_query(
        """
        SELECT 
            DATE(ml.eaten_at) as day,
            SUM(COALESCE(m.calories, fi.calories) * ml.servings) as calories
        FROM meal_log ml
        LEFT JOIN meal m ON ml.meal_id = m.meal_id
        LEFT JOIN food_item fi ON ml.food_item_id = fi.food_item_id
        WHERE ml.user_id = :user_id
        AND ml.eaten_at >= DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
        GROUP BY day
        ORDER BY day ASC
        """,
        {"user_id": user_id},
    )

    data_map = {row["day"]: float(row["calories"]) for row in rows}

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())

    result = []

    for i in range(today.weekday() + 1):
        current_day = (start_of_week + timedelta(days=i)).date()

        calories = data_map.get(current_day, 0)

        result.append({"day": current_day.strftime("%a"), "calories": calories})

    return result
