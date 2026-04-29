from . import chat_bp
from flask import session, request, jsonify
from app.services.chat.getConvMessages import getConvMessages
from app.services.chat.markRead import markAsRead


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
  401:
    description: Unauthorized
"""
    conv_id = request.args.get("conv_id")
    print("conv_id: ", conv_id)
    user_id = session.get("user_id")

    messages = getConvMessages(conv_id, user_id)

    markAsRead(user_id, conv_id)

    if not user_id:
        print("Error")
        return {"error": "Unauthorized"}, 401

    return jsonify(messages), 200
