from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def get_todays_meals(user_id, meal_plan_id, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)

    day_of_week = datetime.now(ZoneInfo(valid_timezone)).strftime("%a")

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
        JOIN meal m
            ON um.meal_id = m.meal_id
        JOIN meal_plan mp
            ON um.meal_plan_id = mp.meal_plan_id
        WHERE um.meal_plan_id = :meal_plan_id
        AND mp.user_id = :user_id
        AND um.day_of_week = :day_of_week
        ORDER BY FIELD(um.meal_type, 'breakfast', 'lunch', 'dinner', 'snack')
        """,
        {
            "meal_plan_id": meal_plan_id,
            "user_id": user_id,
            "day_of_week": day_of_week,
        },
        fetch=True,
        commit=False,
    )

    return rows
