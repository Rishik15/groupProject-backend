from app.services import run_query

def getPendingRequests(coach_id: int):
    results = run_query(
        """
        SELECT 
            ucc.contract_id,
            ucc.user_id,
            ucc.start_date,
            ucc.contract_text,
            ui.first_name,
            ui.last_name
        FROM user_coach_contract ucc
        JOIN users_immutables ui ON ui.user_id = ucc.user_id
        WHERE ucc.coach_id = :coach_id
        AND ucc.active = 1
        AND ucc.end_date IS NULL
        ORDER BY ucc.created_at DESC
        """,
        {"coach_id": coach_id},
    )

    return results