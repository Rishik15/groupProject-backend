from app.services import run_query


def mark_notification_as_read(user_id: int, notif_id: int, mode: str):
    run_query(
        """
        UPDATE notification
        SET is_read = TRUE
        WHERE notification_id = :notif_id
        AND user_id = :user_id
        AND mode = :mode
        """,
        {
            "notif_id": notif_id,
            "user_id": user_id,
            "mode": mode,
        },
        fetch=False,
        commit=True,
    )
