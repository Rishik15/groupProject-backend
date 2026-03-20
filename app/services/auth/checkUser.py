from app.services import run_query


def checkUserExists(user_id=None, email=None):

    if user_id:
        query = """
        SELECT user_id
        FROM users_immutables
        WHERE user_id = :value
        LIMIT 1
        """
        params = {"value": user_id}

    elif email:
        query = """
        SELECT user_id
        FROM users_immutables
        WHERE email = :value
        LIMIT 1
        """
        params = {"value": email}

    else:
        return False

    result = run_query(query, params)
    return bool(result)
