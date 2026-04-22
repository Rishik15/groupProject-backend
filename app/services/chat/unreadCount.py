from sys import exception

from app.services import run_query


def getUnreadCount(user_id: int, conv_id: int):
    query = """
        SELECT unread_count as unreadCount
        FROM conversation_member
        WHERE user_id = :user_id
        AND conversation_id = :conv_id
    """

    result = run_query(query, {"user_id": user_id, "conv_id": conv_id})

    if result:
        return result[0]["unreadCount"]

    return 0
