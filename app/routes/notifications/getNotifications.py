from . import notify_bp
from flask import jsonify, session
from app.services.notifications.get_Notifications import get_user_notifications
from app.services.notifications.getUnreadCount import get_unread_count


@notify_bp.route("/getNotifications", methods=["GET"])
def getNotifications():
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "User not authenticated"}, 401

    notifications = get_user_notifications(user_id)
    count = get_unread_count(user_id)

    return jsonify({"notifications": notifications, "count": count}), 200
