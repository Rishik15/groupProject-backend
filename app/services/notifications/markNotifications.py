from app.services import run_query


def mark_notification_as_read(user_id: int, notif_id: int):
    run_query(
        """
        UPDATE notification
        SET is_read = TRUE
        WHERE notification_id = :notif_id
        AND user_id = :user_id
        """,
        {
            "notif_id": notif_id,
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )
