from app.services import run_query


def create_meal_plan(user_id, plan_name, meals, start_date=None, end_date=None):
    meal_plan_id = run_query(
        """
        INSERT INTO meal_plan
        (
            user_id,
            plan_name,
            start_date,
            end_date
        )
        VALUES
        (
            :user_id,
            :plan_name,
            :start_date,
            :end_date
        )
        """,
        {
            "user_id": user_id,
            "plan_name": plan_name,
            "start_date": start_date,
            "end_date": end_date,
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    if not meal_plan_id:
        raise ValueError("Failed to create meal plan")

    if not meals:
        return meal_plan_id

    meal_ids = []
    for meal in meals:
        meal_id = meal.get("meal_id")

        if meal_id and meal_id not in meal_ids:
            meal_ids.append(meal_id)

    if not meal_ids:
        return meal_plan_id

    placeholders = []
    params = {}

    for index, meal_id in enumerate(meal_ids):
        key = f"id_{index}"
        placeholders.append(f":{key}")
        params[key] = meal_id

    meal_macros = run_query(
        f"""
        SELECT meal_id, calories
        FROM meal
        WHERE meal_id IN ({", ".join(placeholders)})
        """,
        params,
        fetch=True,
        commit=False,
    )

    calories_map = {}

    for row in meal_macros:
        calories_map[row["meal_id"]] = row["calories"]

    total_calories = 0

    for meal in meals:
        meal_id = meal.get("meal_id")
        day = meal.get("day_of_week")
        meal_type = meal.get("meal_type")
        servings = float(meal.get("servings", 1.0))

        if not meal_id or not day or not meal_type:
            continue

        run_query(
            """
            INSERT INTO user_meal
            (
                meal_id,
                meal_plan_id,
                meal_type,
                servings,
                day_of_week
            )
            VALUES
            (
                :meal_id,
                :meal_plan_id,
                :meal_type,
                :servings,
                :day_of_week
            )
            """,
            {
                "meal_id": meal_id,
                "meal_plan_id": meal_plan_id,
                "meal_type": meal_type,
                "servings": servings,
                "day_of_week": day,
            },
            fetch=False,
            commit=True,
        )

        if meal_id in calories_map:
            total_calories += int(float(calories_map[meal_id]) * servings)

    run_query(
        """
        UPDATE meal_plan
        SET total_calories = :total_calories
        WHERE meal_plan_id = :meal_plan_id
        """,
        {
            "total_calories": total_calories,
            "meal_plan_id": meal_plan_id,
        },
        fetch=False,
        commit=True,
    )

    return meal_plan_id
