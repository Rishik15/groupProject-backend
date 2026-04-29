from app.services import run_query


def update_meal_plan(
    user_id,
    meal_plan_id,
    plan_name=None,
    start_date=None,
    end_date=None,
    add_meals=None,
    remove_meals=None,
    update_servings=None,
):
    owner_check = run_query(
        """
        SELECT meal_plan_id
        FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id
        AND user_id = :user_id
        """,
        {
            "meal_plan_id": meal_plan_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not owner_check:
        raise PermissionError("Meal plan not found or does not belong to this user")

    if plan_name is not None or start_date is not None or end_date is not None:
        fields = []
        params = {
            "meal_plan_id": meal_plan_id,
            "user_id": user_id,
        }

        if plan_name is not None:
            cleaned_name = plan_name.strip()

            if not cleaned_name:
                raise ValueError("Plan name cannot be empty")

            fields.append("plan_name = :plan_name")
            params["plan_name"] = cleaned_name

        if start_date is not None:
            fields.append("start_date = :start_date")
            params["start_date"] = start_date

        if end_date is not None:
            fields.append("end_date = :end_date")
            params["end_date"] = end_date

        if fields:
            update_query = f"""
            UPDATE meal_plan
            SET {", ".join(fields)}
            WHERE meal_plan_id = :meal_plan_id
            AND user_id = :user_id
            """

            run_query(update_query, params, fetch=False, commit=True)

    for meal in remove_meals or []:
        meal_id = meal.get("meal_id")
        day_of_week = meal.get("day_of_week")
        meal_type = meal.get("meal_type")

        if not meal_id or not day_of_week or not meal_type:
            continue

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
                "meal_id": meal_id,
                "day_of_week": day_of_week,
                "meal_type": meal_type,
            },
            fetch=False,
            commit=True,
        )

    for meal in add_meals or []:
        meal_id = meal.get("meal_id")
        day_of_week = meal.get("day_of_week")
        meal_type = meal.get("meal_type")
        servings = float(meal.get("servings", 1.0))

        if not meal_id or not day_of_week or not meal_type:
            continue

        if servings <= 0:
            raise ValueError("Servings must be greater than 0")

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
            ON DUPLICATE KEY UPDATE
                servings = VALUES(servings)
            """,
            {
                "meal_id": meal_id,
                "meal_plan_id": meal_plan_id,
                "meal_type": meal_type,
                "servings": servings,
                "day_of_week": day_of_week,
            },
            fetch=False,
            commit=True,
        )

    for meal in update_servings or []:
        meal_id = meal.get("meal_id")
        day_of_week = meal.get("day_of_week")
        meal_type = meal.get("meal_type")
        servings = float(meal.get("servings", 1.0))

        if not meal_id or not day_of_week or not meal_type:
            continue

        if servings <= 0:
            raise ValueError("Servings must be greater than 0")

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
                "meal_id": meal_id,
                "day_of_week": day_of_week,
                "meal_type": meal_type,
                "servings": servings,
            },
            fetch=False,
            commit=True,
        )

    meal_count_result = run_query(
        """
        SELECT COUNT(*) AS meal_count
        FROM user_meal
        WHERE meal_plan_id = :meal_plan_id
        """,
        {
            "meal_plan_id": meal_plan_id,
        },
        fetch=True,
        commit=False,
    )

    meal_count = int(meal_count_result[0]["meal_count"] or 0)

    if meal_count == 0:
        run_query(
            """
            DELETE FROM event
            WHERE user_id = :user_id
            AND event_type = 'meal'
            AND event_date BETWEEN
                COALESCE((SELECT start_date FROM meal_plan WHERE meal_plan_id = :meal_plan_id), event_date)
                AND
                COALESCE((SELECT end_date FROM meal_plan WHERE meal_plan_id = :meal_plan_id), event_date)
            """,
            {
                "user_id": user_id,
                "meal_plan_id": meal_plan_id,
            },
            fetch=False,
            commit=True,
        )

        run_query(
            """
            DELETE FROM meal_plan
            WHERE meal_plan_id = :meal_plan_id
            AND user_id = :user_id
            """,
            {
                "meal_plan_id": meal_plan_id,
                "user_id": user_id,
            },
            fetch=False,
            commit=True,
        )

        return {
            "meal_plan_id": meal_plan_id,
            "total_calories": 0,
            "deleted": True,
        }

    totals = run_query(
        """
        SELECT COALESCE(SUM(m.calories * um.servings), 0) AS total_calories
        FROM user_meal um
        JOIN meal m ON um.meal_id = m.meal_id
        WHERE um.meal_plan_id = :meal_plan_id
        """,
        {
            "meal_plan_id": meal_plan_id,
        },
        fetch=True,
        commit=False,
    )

    total_calories = int(float(totals[0]["total_calories"] or 0))

    run_query(
        """
        UPDATE meal_plan
        SET total_calories = :total_calories
        WHERE meal_plan_id = :meal_plan_id
        AND user_id = :user_id
        """,
        {
            "total_calories": total_calories,
            "meal_plan_id": meal_plan_id,
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )

    return {
        "meal_plan_id": meal_plan_id,
        "total_calories": total_calories,
        "deleted": False,
    }
