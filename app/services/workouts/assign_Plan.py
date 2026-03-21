
from app.services import run_query


def assign_plan_to_user(user_id, plan_id):
    # step 5 of UC 4.2 -- creates a coach_assignment_log entry
    # uses system user (1) as the coach_id since no coach is involved
    query = """
        INSERT INTO coach_assignment_log
            (coach_id, user_id, assigned_type, workout_plan_id, assigned_at, note)
        VALUES
            (1, :user_id, 'workout_plan', :plan_id, NOW(), 'Self-assigned from predefined plan library')
    """
    params = {
        "user_id": user_id,
        "plan_id": plan_id
    }
    run_query(query, params=params, fetch=False, commit=True)