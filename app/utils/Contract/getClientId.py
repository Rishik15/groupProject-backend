from app.services import run_query


def getClientIdFromContract(contract_id, coach_id):
    query = """
        SELECT ucc.user_id as client_id
        FROM user_coach_contract ucc
        WHERE ucc.contract_id = :contract_id
        AND ucc.coach_id = :coach_id
        LIMIT 1
    """

    result = run_query(
        query=query,
        params={
            "contract_id": contract_id,
            "coach_id": coach_id,
        },
        fetch=True,
        commit=False,
    )

    if not result:
        return None

    return result[0]["client_id"]
