from app.services import run_query


def getCoachModeActivated(user_id: int) -> bool:
    application = run_query(
        """
        SELECT status, activated_at
        FROM coach_application
        WHERE user_id = :user_id
        LIMIT 1
        """,
        {"user_id": user_id},
    )

    if application:
        row = application[0]

        if row.get("status") == "approved":
            return bool(row.get("activated_at"))

        return False

    existing_coach = run_query(
        """
        SELECT coach_id
        FROM coach
        WHERE coach_id = :user_id
        LIMIT 1
        """,
        {"user_id": user_id},
    )

    return bool(existing_coach)


def activateCoachMode(user_id: int):
    run_query(
        """
        UPDATE coach_application
        SET activated_at = COALESCE(activated_at, NOW())
        WHERE user_id = :user_id
        AND status = 'approved'
        """,
        {"user_id": user_id},
        fetch=False,
        commit=True,
    )
