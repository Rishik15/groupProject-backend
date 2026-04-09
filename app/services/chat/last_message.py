from app.services import run_query


def get_last_message(user_id, other_user_id):

    query = """
        SELECT 
            m.content,
            cm1.conversation_id
        FROM conversation_member cm1
        JOIN conversation_member cm2
            ON cm1.conversation_id = cm2.conversation_id
        JOIN message m
            ON m.conversation_id = cm1.conversation_id
        WHERE cm1.user_id = :user_id
        AND cm2.user_id = :other_user_id
        AND m.deleted_at IS NULL
        ORDER BY m.sent_at DESC
        LIMIT 1
    """

    result = run_query(query, {"user_id": user_id, "other_user_id": other_user_id})

    if result:
        return {
            "lastMessage": result[0]["content"],
            "conversationId": result[0]["conversation_id"],
        }

    return {"lastMessage": None, "conversationId": None}
