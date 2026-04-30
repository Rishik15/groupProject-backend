from app.services import run_query


def get_contract_status(user_id: int, coach_id: int):
    result = run_query(
        """
        SELECT active, end_date
        FROM user_coach_contract
        WHERE user_id = :user_id
          AND coach_id = :coach_id
        ORDER BY created_at DESC
        LIMIT 1
        """,
        {
            "user_id": int(user_id),
            "coach_id": int(coach_id),
        },
        fetch=True,
        commit=False,
    )

    if not result:
        return "none"

    row = result[0]

    if row["active"] == 1:
        return "active"

    if row["active"] == 0 and row["end_date"] is None:
        return "pending"

    return "closed"


def get_client_active_coach(user_id: int):
    result = run_query(
        """
        SELECT
            ucc.contract_id,
            ucc.coach_id,
            CONCAT(ui.first_name, ' ', ui.last_name) AS coach_name
        FROM user_coach_contract ucc
        JOIN users_immutables ui
            ON ui.user_id = ucc.coach_id
        WHERE ucc.user_id = :user_id
          AND ucc.active = 1
        ORDER BY ucc.created_at DESC
        LIMIT 1
        """,
        {
            "user_id": int(user_id),
        },
        fetch=True,
        commit=False,
    )

    if not result:
        return None

    return result[0]
