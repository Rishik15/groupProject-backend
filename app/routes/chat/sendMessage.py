from . import chat_bp
from flask import session, request
from app.services.chat.sendMessage import addMessage


@chat_bp.route("/sendMessage", methods=["POST"])
def sendMessage():
    data = request.get_json()

    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    message = data.get("message")
    conv_id = data.get("conv_id")

    if not message or not conv_id:
        return {"error": "Missing data"}, 400

    msg = addMessage(user_id, conv_id, message)

    return {"message": msg}, 200
