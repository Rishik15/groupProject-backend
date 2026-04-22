from . import notify_bp
from flask import jsonify, session
from app.services.notifications.get_Notifications import get_user_notifications
from app.services.notifications.getUnreadCount import get_unread_count
from flask import request

@notify_bp.route("/getNotifications", methods=["GET"])
def getNotifications():
    user_id = session.get("user_id")
    mode = request.args.get("mode")  

    if not user_id:
        return {"error": "User not authenticated"}, 401

    if not mode:
        return {"error": "Missing mode"}, 400

    notifications = get_user_notifications(user_id, mode)
    count = get_unread_count(user_id, mode)

    return jsonify({"notifications": notifications, "count": count}), 200