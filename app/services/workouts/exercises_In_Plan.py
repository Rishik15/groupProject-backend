# app/services/client/workout_service.py
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
            e.video_url
        FROM plan_exercise pe
        JOIN exercise e ON pe.exercise_id = e.exercise_id
        WHERE pe.plan_id = :plan_id
        ORDER BY pe.order_in_workout ASC
    """
    params = {"plan_id": plan_id}
    return run_query(query, params=params, fetch=True, commit=False)