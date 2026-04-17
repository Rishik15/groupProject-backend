from app.services import run_query


def create_workout_plan(user_id, plan_name, exercises, description):
    
    user = run_query(
        "SELECT first_name, last_name FROM users_immutables WHERE user_id = :user_id",
        {"user_id": user_id},
        fetch=True,
        commit=False
    )
    full_name = f"{user[0]['first_name']} {user[0]['last_name']}" if user else "Unknown"
    description = f"This workout plan was created by {full_name}"
    
    # step 1 insert the plan name into workout_plan
    run_query(
        "INSERT INTO workout_plan (plan_name) VALUES (:plan_name)",
        {"plan_name": plan_name},
        fetch=False,
        commit=True
    )

    # step 2 get the new planID
    result = run_query(
        "SELECT plan_id FROM workout_plan WHERE plan_name = :plan_name",
        {"plan_name": plan_name},
        fetch=True,
        commit=False
    )
    plan_id = result[0]["plan_id"]

    # step 3 insert into workout_plan_template to mark user as author
    run_query(
        """
        INSERT INTO workout_plan_template (plan_id, author_user_id, is_public, description)
        VALUES (:plan_id, :user_id, 0, :description)
        """,
        {"plan_id": plan_id, "user_id": user_id, "description": description}, 
        fetch=False,
        commit=True
    )

    # step 4 — insert each exercise into plan_exercise
    for i, ex in enumerate(exercises):
        run_query(
            """
            INSERT INTO plan_exercise
                (plan_id, exercise_id, order_in_workout, sets_goal, reps_goal)
            VALUES
                (:plan_id, :exercise_id, :order_in_workout, :sets_goal, :reps_goal)
            """,
            {
                "plan_id": plan_id,
                "exercise_id": ex["exercise_id"],
                "order_in_workout": i + 1,
                "sets_goal": ex.get("sets"),
                "reps_goal": ex.get("reps")
            },
            fetch=False,
            commit=True
        )

    return plan_id