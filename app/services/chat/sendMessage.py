from app.services import run_query


def addMessage(sender, conv_id, message):
    run_query(
        """
        INSERT INTO message (conversation_id, sender_user_id, content)
        VALUES (:conv_id, :sender, :message)
        """,
        {"conv_id": conv_id, "sender": sender, "message": message},
        fetch=False,
        commit=True,
    )

    result = run_query(
        """
        SELECT message_id, conversation_id, sender_user_id, content, sent_at
        FROM message
        WHERE conversation_id = :conv_id
        ORDER BY sent_at DESC
        LIMIT 1
        """,
        {"conv_id": conv_id},
    )

    msg = result[0] if result else None

    if msg:
        msg["sent_at"] = msg["sent_at"].isoformat()  # ✅ FIX

    return msg