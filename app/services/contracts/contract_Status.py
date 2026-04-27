from app.services import run_query
from datetime import date


def get_contract_status(user_id, coach_id):
    result = run_query(
        """
        SELECT active, end_date
        FROM user_coach_contract
        WHERE user_id = :user_id
        AND coach_id = :coach_id
        ORDER BY created_at DESC
        LIMIT 1
        """,
        {"user_id": user_id, "coach_id": coach_id},
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
