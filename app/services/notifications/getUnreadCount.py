from app.services import run_query


def get_unread_count(user_id: int):
    result = run_query(
        """
        SELECT COUNT(*) AS count
        FROM notification
        WHERE user_id = :user_id
        AND is_read = FALSE
        """,
        {"user_id": user_id},
    )

    return result[0]["count"]
