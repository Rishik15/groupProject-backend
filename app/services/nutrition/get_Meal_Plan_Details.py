from app.services import run_query


def get_meal_plan_detail(plan_id: int):
    """Returns a meal plan with its full week of meals."""
    plan = run_query(
        """
        SELECT
            meal_plan_id,
            plan_name,
            total_calories
        FROM meal_plan
        WHERE meal_plan_id = :plan_id
        """,
        {"plan_id": plan_id},
        fetch=True, commit=False
    )

    if not plan:
        return None

    meals = run_query(
        """
        SELECT
            m.meal_id,
            m.name,
            m.calories,
            m.protein,
            m.carbs,
            m.fats,
            um.meal_type,
            um.day_of_week,
            um.servings
        FROM user_meal um
        JOIN meal m ON um.meal_id = m.meal_id
        WHERE um.meal_plan_id = :plan_id
        ORDER BY
            FIELD(um.day_of_week, 'Mon','Tue','Wed','Thu','Fri','Sat','Sun'),
            FIELD(um.meal_type, 'breakfast','lunch','dinner','snack')
        """,
        {"plan_id": plan_id},
        fetch=True, commit=False
    )

    return {
        "meal_plan_id": plan[0]["meal_plan_id"],
        "plan_name": plan[0]["plan_name"],
        "total_calories": plan[0]["total_calories"],
        "meals": meals
    }