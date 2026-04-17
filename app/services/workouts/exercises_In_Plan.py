# app/services/workouts/exercises_In_Plan.py
from app.services import run_query

def get_workout_plan_exercises(plan_id):
    query = """
        SELECT
            pe.order_in_workout,
            pe.sets_goal,
            pe.reps_goal,
            pe.weight_goal,
            e.exercise_name,
            e.equipment,
            e.video_url,
            wd.day_order,
            wd.day_label
        FROM workout_day wd
        JOIN plan_exercise pe ON pe.day_id = wd.day_id
        JOIN exercise e ON pe.exercise_id = e.exercise_id
        WHERE wd.plan_id = :plan_id
        ORDER BY wd.day_order ASC, pe.order_in_workout ASC
    """
    params = {"plan_id": plan_id}
    return run_query(query, params=params, fetch=True, commit=False)