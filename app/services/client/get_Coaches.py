from app.services import run_query

def getUsersCoaches(user_id):
    query = """
    SELECT 
        c.coach_id,
        CONCAT(ui.first_name, ' ', ui.last_name) AS full_name
    FROM user_coach_contract ucc
    JOIN coach c ON ucc.coach_id = c.coach_id
    JOIN users_immutables ui ON c.coach_id = ui.user_id
    WHERE ucc.user_id = :uid 
        AND ucc.active = 1;
    """

    try: 
        results = run_query(query, {"uid": user_id}, fetch=True, commit=False)
        return results if results else []
    except Exception as e:
        raise Exception(f"Failed to fetch user's coaches: {str(e)}")