from sys import exception

from app.services import run_query

def getUnreadCount(user_id :int):
    query = '''
            SELECT unread_count as unreadCount
            FROM conversation_member as cm
            WHERE cm.user_id = :user_id    
            '''

    count = run_query(query, {"user_id": user_id})

    return count