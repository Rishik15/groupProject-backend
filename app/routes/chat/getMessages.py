from . import chat_bp
from flask import session, request, jsonify
from app.services.chat.getConvMessages import getConvMessages
from app.services.chat.markRead import markAsRead


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@chat_bp.route("/getMessages", methods=["GET"])
def getMessages():
    """
    Get conversation messages
    ---
    tags:
      - chat
    parameters:
      - name: conv_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Messages fetched
      400:
        description: Missing conv_id
      401:
        description: Unauthorized
    """
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    conv_id = request.args.get("conv_id")

    if not conv_id:
        return {"error": "conv_id is required"}, 400

    messages = getConvMessages(
        conv_id=conv_id,
        user_id=int(user_id),
        user_timezone=_get_session_timezone(),
    )

    markAsRead(int(user_id), conv_id)

    return jsonify(messages), 200
