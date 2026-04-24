from app.services import run_query


def get_user_notifications(user_id: int, mode: str):
    result = run_query(
        """
        SELECT 
            notification_id AS id,
            type,
            conversation_id,
            title,
            body,
            is_read,
            created_at
        FROM notification
        WHERE user_id = :user_id
        AND is_read = FALSE
        AND mode = :mode
        ORDER BY created_at DESC
        LIMIT 50
        """,
        {"user_id": user_id, "mode": mode},
    )

    return [
        {
            "id": row["id"],
            "type": row["type"],
            "conversationId": row["conversation_id"],
            "title": row["title"],
            "body": row["body"],
            "is_read": row["is_read"],
        }
        for row in result
    ]