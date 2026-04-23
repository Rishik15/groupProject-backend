from app.services import run_query

def getConvMessages(conv_id, user_id):

    query = """
        SELECT 
            m.message_id,
            m.sender_user_id,
            m.content,
            m.sent_at
        FROM message m
        JOIN conversation_member cm
            ON cm.conversation_id = m.conversation_id
        WHERE m.conversation_id = :conv_id
        AND cm.user_id = :user_id
        AND m.deleted_at IS NULL
        ORDER BY m.sent_at ASC
    """

    result = run_query(query, {
        "conv_id": conv_id,
        "user_id": user_id
    })

    messages = []

    for row in result:
        messages.append({
            "id": row["message_id"],
            "text": row["content"],
            "timestamp": row["sent_at"],
            "type": "sent" if row["sender_user_id"] == user_id else "received"
        })

    return messages