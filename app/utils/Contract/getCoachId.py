from app.services import run_query


def getCoachIdFromContract(client_id):
    query = """
        SELECT ucc.coach_id as coach_id
        FROM user_coach_contract ucc
        WHERE ucc.user_id = :client_id
        LIMIT 1
    """

    result = run_query(
        query=query,
        params={"client": client_id},
        fetch=True,
        commit=False,
    )

    if not result:
        return None

    return result[0]["coach_id"]
