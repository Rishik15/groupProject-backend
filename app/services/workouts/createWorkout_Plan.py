from app.services import run_query


def create_workout_plan(user_id, plan_name, days, description):

    plan_id = run_query(
        "INSERT INTO workout_plan (plan_name) VALUES (:plan_name)",
        {"plan_name": plan_name},
        fetch=False,
        commit=True,
        return_lastrowid=True
    )

    run_query(
        """
        INSERT INTO workout_plan_template (plan_id, author_user_id, is_public, description)
        VALUES (:plan_id, :user_id, 0, :description)
        """,
        {"plan_id": plan_id, "user_id": user_id, "description": description},
        fetch=False,
        commit=True
    )

    for day_order, day in enumerate(days, start=1):
        day_label = day.get("day_label", f"Day {day_order}")
        exercises = day.get("exercises", [])

        day_id = run_query(
            """
            INSERT INTO workout_day (plan_id, day_order, day_label)
            VALUES (:plan_id, :day_order, :day_label)
            """,
            {"plan_id": plan_id, "day_order": day_order, "day_label": day_label},
            fetch=False,
            commit=True,
            return_lastrowid=True
        )

        for order_in_workout, ex in enumerate(exercises, start=1):
            run_query(
                """
                INSERT INTO plan_exercise
                    (day_id, exercise_id, order_in_workout, sets_goal, reps_goal)
                VALUES
                    (:day_id, :exercise_id, :order_in_workout, :sets_goal, :reps_goal)
                """,
                {
                    "day_id":           day_id,
                    "exercise_id":      ex["exercise_id"],
                    "order_in_workout": order_in_workout,
                    "sets_goal":        ex.get("sets"),
                    "reps_goal":        ex.get("reps")
                },
                fetch=False,
                commit=True
            )

    return plan_id