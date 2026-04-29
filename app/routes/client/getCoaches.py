from . import client_bp
from flask import jsonify, request, session
from app.services.client.get_Coaches import getUsersCoaches

@client_bp.route("/getCoaches", methods=["GET"]) # Added .route here
def getCoaches():
    """
Get user's coaches
---
tags:
  - client
responses:
  200:
    description: List of coaches
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"Error": "User authentication required"}), 401
        
    try:
        result = getUsersCoaches(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500