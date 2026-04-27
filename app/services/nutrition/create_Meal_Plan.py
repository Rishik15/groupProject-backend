from app.services import run_query


def create_meal_plan(user_id, plan_name, meals, start_date=None, end_date=None):

    # Insert the meal plan header
    run_query(
        """
        INSERT INTO meal_plan (user_id, plan_name, start_date, end_date)
        VALUES (:user_id, :plan_name, :start_date, :end_date)
        """,
        {
            "user_id": user_id,
            "plan_name": plan_name,
            "start_date": start_date,
            "end_date": end_date
        },
        fetch=False, commit=True
    )

    # Get the ID of the row we just inserted
    result = run_query(
        "SELECT LAST_INSERT_ID() AS meal_plan_id",
        fetch=True, commit=False
    )
    meal_plan_id = result[0]["meal_plan_id"]

    if not meals:
        return meal_plan_id

    # Collect unique meal_ids
    meal_ids = []
    for m in meals:
        if m["meal_id"] not in meal_ids:
            meal_ids.append(m["meal_id"])

    # Build placeholders for IN clause
    placeholders = ""
    params = {}
    for i in range(len(meal_ids)):
        if i > 0:
            placeholders += ", "
        placeholders += f":id_{i}"
        params[f"id_{i}"] = meal_ids[i]

    # Fetch calories for each meal
    meal_macros = run_query(
        f"""
        SELECT meal_id, calories
        FROM meal
        WHERE meal_id IN ({placeholders})
        """,
        params,
        fetch=True, commit=False
    )

    # Build calories lookup
    calories_map = {}
    for row in meal_macros:
        calories_map[row["meal_id"]] = row["calories"]

    # Insert user_meal rows and calculate total calories
    total_calories = 0
    for m in meals:
        meal_id   = m["meal_id"]
        day       = m["day_of_week"]
        meal_type = m["meal_type"]
        servings  = float(m.get("servings", 1.0))

        run_query(
            """
            INSERT INTO user_meal (meal_id, meal_plan_id, meal_type, servings, day_of_week)
            VALUES (:meal_id, :meal_plan_id, :meal_type, :servings, :day_of_week)
            """,
            {
                "meal_id": meal_id,
                "meal_plan_id": meal_plan_id,
                "meal_type": meal_type,
                "servings": servings,
                "day_of_week": day
            },
            fetch=False, commit=True
        )

        if meal_id in calories_map:
            total_calories += int(calories_map[meal_id] * servings)

    # Update total_calories on the plan
    run_query(
        """
        UPDATE meal_plan SET total_calories = :total_calories
        WHERE meal_plan_id = :meal_plan_id
        """,
        {"total_calories": total_calories, "meal_plan_id": meal_plan_id},
        fetch=False, commit=True
    )

    return meal_plan_id