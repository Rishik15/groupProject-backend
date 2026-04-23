from app.services import run_query


def get_unread_count(user_id: int, mode: str):
    result = run_query(
        """
        SELECT COUNT(*) AS count
        FROM notification
        WHERE user_id = :user_id
        AND is_read = FALSE
        AND mode = :mode
        """,
        {"user_id": user_id, "mode": mode},
    )

    return result[0]["count"]
