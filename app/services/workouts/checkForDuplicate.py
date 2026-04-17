from app.services import run_query

def get_plan_conflict(user_id, exercises, plan_name):
    # Check name conflict
    name_conflict = run_query(
        """
        SELECT 1
        FROM workout_plan_template wpt
        JOIN workout_plan wp ON wp.plan_id = wpt.plan_id
        WHERE wpt.author_user_id = :user_id
          AND wp.plan_name = :plan_name
        LIMIT 1
        """,
        {"user_id": user_id, "plan_name": plan_name},
        fetch=True,
        commit=False
    )

    if name_conflict:
        return "name"

    # Check structure conflict
    user_plans = run_query(
        """
        SELECT plan_id
        FROM workout_plan_template
        WHERE author_user_id = :user_id
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False
    )

    for plan in user_plans:
        existing_exercises = run_query(
            """
            SELECT exercise_id, sets_goal, reps_goal, order_in_workout
            FROM plan_exercise
            WHERE plan_id = :plan_id
            ORDER BY order_in_workout ASC
            """,
            {"plan_id": plan["plan_id"]},
            fetch=True,
            commit=False
        )

        if same_exercise_structure(existing_exercises, exercises):
            return "structure"

    return None


def same_exercise_structure(existing_exercises, incoming_exercises):
    if len(existing_exercises) != len(incoming_exercises):
        return False

    for existing_ex, incoming_ex in zip(existing_exercises, incoming_exercises):
        if (
            existing_ex["exercise_id"] != incoming_ex["exercise_id"] or existing_ex["sets_goal"] != incoming_ex.get("sets") 
            or existing_ex["reps_goal"] != incoming_ex.get("reps")
        ):
            return False

    return True