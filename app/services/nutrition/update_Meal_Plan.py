from app.services import run_query

def update_meal_plan(user_id, meal_plan_id, plan_name=None, start_date=None, end_date=None, add_meals=None, remove_meals=None, update_servings=None):

    # Verify the plan belongs to this user
    owner_check = run_query(
        """
        SELECT meal_plan_id FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id AND user_id = :user_id
        """,
        {"meal_plan_id": meal_plan_id, "user_id": user_id},
        fetch=True, commit=False
    )

    if not owner_check:
        raise PermissionError("Meal plan not found or does not belong to this user")

    # Update plan header if any fields provided
    if plan_name or start_date or end_date:
        fields = []
        params = {"meal_plan_id": meal_plan_id}

        if plan_name:
            fields.append("plan_name = :plan_name")
            params["plan_name"] = plan_name

        if start_date:
            fields.append("start_date = :start_date")
            params["start_date"] = start_date

        if end_date:
            fields.append("end_date = :end_date")
            params["end_date"] = end_date

        update_query = "UPDATE meal_plan SET " + ", ".join(fields) + " WHERE meal_plan_id = :meal_plan_id"

        run_query(update_query, params, fetch=False, commit=True)

    # Remove meals
    if remove_meals:
        for m in remove_meals:
            run_query(
                """
                DELETE FROM user_meal
                WHERE meal_plan_id = :meal_plan_id
                AND meal_id = :meal_id
                AND day_of_week = :day_of_week
                AND meal_type = :meal_type
                """,
                {
                    "meal_plan_id": meal_plan_id,
                    "meal_id": m["meal_id"],
                    "day_of_week": m["day_of_week"],
                    "meal_type": m["meal_type"]
                },
                fetch=False, commit=True
            )

    # Add meals
    if add_meals:
        for m in add_meals:
            run_query(
                """
                INSERT INTO user_meal (meal_id, meal_plan_id, meal_type, servings, day_of_week)
                VALUES (:meal_id, :meal_plan_id, :meal_type, :servings, :day_of_week)
                """,
                {
                    "meal_id": m["meal_id"],
                    "meal_plan_id": meal_plan_id,
                    "meal_type": m["meal_type"],
                    "servings": float(m.get("servings", 1.0)),
                    "day_of_week": m["day_of_week"]
                },
                fetch=False, commit=True
            )

    # Update servings
    if update_servings:
        for m in update_servings:
            run_query(
                """
                UPDATE user_meal
                SET servings = :servings
                WHERE meal_plan_id = :meal_plan_id
                AND meal_id = :meal_id
                AND day_of_week = :day_of_week
                AND meal_type = :meal_type
                """,
                {
                    "meal_plan_id": meal_plan_id,
                    "meal_id": m["meal_id"],
                    "day_of_week": m["day_of_week"],
                    "meal_type": m["meal_type"],
                    "servings": float(m["servings"])
                },
                fetch=False, commit=True
            )

    # Recalculate total_calories from current user_meal rows
    totals = run_query(
        """
        SELECT SUM(m.calories * um.servings) AS total_calories
        FROM user_meal um
        JOIN meal m ON um.meal_id = m.meal_id
        WHERE um.meal_plan_id = :meal_plan_id
        """,
        {"meal_plan_id": meal_plan_id},
        fetch=True, commit=False
    )

    total_calories = totals[0]["total_calories"] if totals[0]["total_calories"] else 0

    run_query(
        """
        UPDATE meal_plan SET total_calories = :total_calories
        WHERE meal_plan_id = :meal_plan_id
        """,
        {"total_calories": int(total_calories), "meal_plan_id": meal_plan_id},
        fetch=False, commit=True
    )