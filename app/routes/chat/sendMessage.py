from . import chat_bp
from flask import session, request
from app.services.chat.sendMessage import addMessage
from app.services.chat.emitMessage import handle_emit_message


@chat_bp.route("/sendMessage", methods=["POST"])
def sendMessage():
    try:
        data = request.get_json()

        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        message = data.get("message")
        conv_id = data.get("conv_id")

        if not message or not conv_id:
            return {"error": "Missing data"}, 400

        msg = addMessage(user_id, conv_id, message)

        handle_emit_message(msg, user_id, conv_id)

        return {"message": msg}, 200

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": "Server crash"}, 500
