from app.services import run_query


def checkUserExists(email):

    query = """
    SELECT user_id
    FROM users_immutables
    WHERE email = :email
    LIMIT 1
    """

    result = run_query(query, {"email": email})

    return bool(result)
