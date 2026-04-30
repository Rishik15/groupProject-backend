from flask import jsonify, session
from . import client_bp
from app.services.client.previous_coaches import get_previous_coaches


@client_bp.route("/getPreviousCoaches", methods=["GET"])
def get_previous_coaches_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        coaches = get_previous_coaches(int(user_id))

        return jsonify(coaches), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
