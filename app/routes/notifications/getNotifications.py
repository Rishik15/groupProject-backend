from . import notify_bp
from flask import jsonify, request, session
from app.services.notifications.get_Notifications import get_user_notifications
from app.services.notifications.getUnreadCount import get_unread_count


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@notify_bp.route("/getNotifications", methods=["GET"])
def getNotifications():
    """
    Get user notifications
    ---
    tags:
      - notifications
    parameters:
      - name: mode
        in: query
        type: string
        required: true
    responses:
      200:
        description: Notifications fetched
        schema:
          type: object
          properties:
            notifications:
              type: array
            count:
              type: integer
      400:
        description: Missing mode
      401:
        description: Unauthorized
    """
    user_id = session.get("user_id")
    mode = request.args.get("mode")

    if not user_id:
        return {"error": "User not authenticated"}, 401

    if not mode:
        return {"error": "Missing mode"}, 400

    notifications = get_user_notifications(
        user_id=int(user_id),
        mode=mode,
        user_timezone=_get_session_timezone(),
    )

    count = get_unread_count(
        user_id=int(user_id),
        mode=mode,
    )

    return (
        jsonify(
            {
                "notifications": notifications,
                "count": count,
            }
        ),
        200,
    )
