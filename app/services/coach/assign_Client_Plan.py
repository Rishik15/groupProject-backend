from app.services import run_query


def assign_plan_to_client(coach_id, client_id, plan_id, note=None):
    contract_check = """
        SELECT contract_id FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND user_id = :client_id
        AND active = 1
    """
    contract = run_query(contract_check, params={"coach_id": coach_id, "client_id": client_id}, fetch=True, commit=False)

    if not contract:
        raise PermissionError("No active contract found between this coach and client")

    query = """
        INSERT INTO coach_assignment_log
            (coach_id, user_id, assigned_type, workout_plan_id, assigned_at, note)
        VALUES
            (:coach_id, :client_id, 'workout_plan', :plan_id, NOW(), :note)
    """
    run_query( query, params={"coach_id": coach_id, "client_id": client_id, "plan_id": plan_id, "note": note}, fetch=False, commit=True)