from app.services import run_query


def markAsRead(user_id, conv_id):
    query = """
        UPDATE conversation_member
        SET unread_count = 0
        WHERE conversation_id = :conv_id
        AND user_id = :user_id
    """

    run_query(
        query, params={"user_id": user_id, "conv_id": conv_id}, fetch=False, commit=True
    )
