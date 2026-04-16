from . import chat_bp
from flask import session, jsonify
from app.services.chat.get_users import get_relevant_users
from app.services.chat.last_message import get_last_message
from app.services.chat.unreadCount import getUnreadCount


from app import online_users, chat_online_users


@chat_bp.route("/get_users", methods=["GET"])
def get_users():

    user_id = session.get("user_id")
    role = session.get("role")

    users = get_relevant_users(user_id, role)

    for user in users:
        chat_data = get_last_message(user_id, user["id"])

        user["lastMessage"] = chat_data["lastMessage"]
        user["conversationId"] = chat_data["conversationId"]

        uid = user["id"]
        user["unreadCount"] = getUnreadCount(user_id)

        user["status"] = "online" if uid in chat_online_users else "offline"

    return jsonify(users or [])
