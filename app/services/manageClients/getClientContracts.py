from app.services import run_query


def getClientContracts(coach_id: int):
    query = """
            SELECT ucc.contract_id, CONCAT(ui.first_name, ' ', ui.last_name) AS name
            FROM user_coach_contract ucc
            JOIN users_immutables ui ON ucc.user_id = ui.user_id
            WHERE ucc.coach_id = :coach_id
            AND ucc.active = 1
        """

    clients = run_query(
        query=query, params={"coach_id": coach_id}, fetch=True, commit=False
    )

    if not clients:
        return []
    else:
        return clients
