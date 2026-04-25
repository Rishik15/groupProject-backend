from app.services import run_query


def getCoachApplicationStatus(user_id: int) -> str:
    application = run_query(
        """
        SELECT status
        FROM coach_application
        WHERE user_id = :user_id
        LIMIT 1
        """,
        {"user_id": user_id},
    )

    if application:
        status = application[0].get("status")

        if status in {"pending", "approved", "rejected"}:
            return status

    existing_coach = run_query(
        """
        SELECT coach_id
        FROM coach
        WHERE coach_id = :user_id
        LIMIT 1
        """,
        {"user_id": user_id},
    )

    if existing_coach:
        return "approved"

    return "none"
