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
        sender_mode = data.get("sender_mode")  

        if not message or not conv_id or not sender_mode:
            return {"error": "Missing data"}, 400

        if sender_mode not in ["client", "coach"]:
            return {"error": "Invalid mode"}, 400

        sender_identity = f"{user_id}:{sender_mode}" 

        msg = addMessage(user_id, conv_id, message)

        handle_emit_message(msg, user_id, conv_id, sender_identity)

        return {"message": msg}, 200

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": "Server crash"}, 500
