from app.services import run_query


def get_pending_requests(coach_id: int):

    rows = run_query(
        """
        SELECT 
            c.contract_id,
            c.user_id,
            u.first_name,
            u.last_name,
            c.start_date,
            c.created_at
        FROM user_coach_contract c
        JOIN users_immutables u ON c.user_id = u.user_id
        WHERE c.coach_id = :coach_id
        AND c.active = 0
        AND c.end_date IS NULL
        ORDER BY c.created_at DESC
        """,
        {"coach_id": coach_id},
    )

    return rows
