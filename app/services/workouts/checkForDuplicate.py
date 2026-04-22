# app/services/workouts/checkForDuplicate.py
from app.services import run_query


def get_plan_conflict(user_id, exercises, plan_name):
    # Check name conflict against plans this user authored
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

    # Check structure conflict: fetch all plans authored by this user
    user_plans = run_query(
        """
        SELECT plan_id FROM workout_plan_template
        WHERE author_user_id = :user_id
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False
    )

    for plan in user_plans:
        # Join through workout_day to get exercises — plan_exercise no longer
        # has plan_id directly (3NF: plan_id lives only in workout_day)
        existing_exercises = run_query(
            """
            SELECT pe.exercise_id, pe.sets_goal, pe.reps_goal, pe.order_in_workout
            FROM workout_day wd
            JOIN plan_exercise pe ON pe.day_id = wd.day_id
            WHERE wd.plan_id = :plan_id
            ORDER BY wd.day_order ASC, pe.order_in_workout ASC
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
            existing_ex["exercise_id"] != incoming_ex["exercise_id"]
            or existing_ex["sets_goal"] != incoming_ex.get("sets")
            or existing_ex["reps_goal"] != incoming_ex.get("reps")
        ):
            return False

    return True