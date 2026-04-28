from app.services import run_query


def assign_plan_to_user(user_id, plan_id, coach_id=1, note=None):
    query = """
        INSERT INTO coach_assignment_log
            (coach_id, user_id, assigned_type, workout_plan_id, assigned_at, note)
        VALUES
            (:coach_id, :user_id, 'workout_plan', :plan_id, NOW(), :note)
    """

    params = {
        "coach_id": coach_id,
        "user_id": user_id,
        "plan_id": plan_id,
        "note": note or "Assigned workout plan",
    }

    run_query(query, params=params, fetch=False, commit=True)

    return {
        "success": True,
        "message": "Workout plan assigned successfully",
        "planId": int(plan_id),
    }
