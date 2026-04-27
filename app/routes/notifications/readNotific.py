from . import notify_bp
from flask import request, session
from app.services.notifications.markNotifications import mark_notification_as_read


@notify_bp.route("/markAsRead", methods=["POST"])
def mark_as_read():
    user_id = session.get("user_id")
    mode = request.args.get("mode")

    if not user_id:
        return {"error": "User not authenticated"}, 401

    data = request.get_json() or {}
    notif_id = data.get("id")

    if notif_id is None or mode is None:
        return {"error": "Missing data"}, 400

    mark_notification_as_read(int(user_id), int(notif_id), mode)

    return {"message": "Marked as read"}, 200
