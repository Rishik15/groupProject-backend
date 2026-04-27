from app.services import run_query
from datetime import datetime


def get_todays_meals(user_id, meal_plan_id):
    day_of_week = datetime.now().strftime("%a")  # Mon, Tue, Wed etc.

    rows = run_query(
        """
        SELECT
            m.meal_id,
            m.name,
            m.calories,
            m.protein,
            m.carbs,
            m.fats,
            um.meal_type,
            um.servings,
            um.day_of_week
        FROM user_meal um
        JOIN meal m ON um.meal_id = m.meal_id
        JOIN meal_plan mp ON um.meal_plan_id = mp.meal_plan_id
        WHERE um.meal_plan_id = :meal_plan_id
        AND mp.user_id = :user_id
        AND um.day_of_week = :day_of_week
        ORDER BY FIELD(um.meal_type, 'breakfast', 'lunch', 'dinner', 'snack')
        """,
        {
            "meal_plan_id": meal_plan_id,
            "user_id": user_id,
            "day_of_week": day_of_week
        },
        fetch=True, commit=False
    )

    return rows