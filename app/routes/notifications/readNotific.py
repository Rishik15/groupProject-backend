from . import notify_bp
from flask import request, session
from app.services.notifications.markNotifications import mark_notification_as_read


@notify_bp.route("/markAsRead", methods=["POST"])
def mark_as_read():
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "User not authenticated"}, 401

    data = request.get_json()
    notif_id = data.get("id")

    if not notif_id:
        return {"error": "Missing notification id"}, 400

    mark_notification_as_read(user_id, notif_id)

    return {"message": "Marked as read"}, 200
