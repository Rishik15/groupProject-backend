from app.services import run_query


def get_coach_clients(coach_id):
    query = """
        SELECT
            u.user_id,
            u.first_name,
            u.last_name,
            u.email,
            c.start_date,
            c.agreed_price
        FROM user_coach_contract c
        JOIN users_immutables u ON c.user_id = u.user_id
        WHERE c.coach_id = :coach_id
        AND c.active = 1
        ORDER BY u.last_name ASC
    """
    return run_query(query, params={"coach_id": coach_id}, fetch=True,commit=False)