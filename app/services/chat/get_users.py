from app.services import run_query


def get_relevant_users(user_id, mode):

    if mode == "coach":
        query = """
            SELECT 
                u.user_id AS id,
                CONCAT(u.first_name, ' ', u.last_name) AS fullName,
                LEFT(u.first_name, 1) AS initial
            FROM user_coach_contract c
            JOIN users_immutables u ON u.user_id = c.user_id
            WHERE c.coach_id = :user_id AND c.active = 1
        """

    else:
        query = """
            SELECT 
                u.user_id AS id,
                CONCAT(u.first_name, ' ', u.last_name) AS fullName,
                LEFT(u.first_name, 1) AS initial
            FROM user_coach_contract c
            JOIN users_immutables u ON u.user_id = c.coach_id
            WHERE c.user_id = :user_id AND c.active = 1
        """

    return run_query(query, {"user_id": user_id})
