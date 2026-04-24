from . import chat_bp
from flask import session, jsonify
from app.services.chat.get_users import get_relevant_users
from app.services.chat.last_message import get_last_message
from app.services.chat.unreadCount import getUnreadCount
from app import chat_online_users

from flask import request


@chat_bp.route("/get_users", methods=["GET"])
def get_users():

    user_id = session.get("user_id")
    mode = request.args.get("mode")

    users = get_relevant_users(user_id, mode)

    opposite_mode = "coach" if mode == "client" else "client"

    for user in users:
        chat_data = get_last_message(user_id, user["id"])

        user["lastMessage"] = chat_data["lastMessage"]
        user["conversationId"] = chat_data["conversationId"]

        uid = user["id"]
        conv_id = user["conversationId"]

        count = getUnreadCount(user_id, conv_id)
        user["unreadCount"] = count

        identity = f"{uid}:{opposite_mode}"

        is_online = identity in chat_online_users and chat_online_users[identity]

        user["status"] = "online" if is_online else "offline"
        user["identity"] = identity

    return jsonify(users or [])
