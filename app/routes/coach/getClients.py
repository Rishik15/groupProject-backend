from . import coach_bp
from flask import request, jsonify, session


@coach_bp.route("/clients", methods=["GET"])
def get_coach_clients():
    coach_id = session.get("user_id")

    if not coach_id:
        return jsonify({"error": "Not logged in"}), 401

    try:
        clients = get_coach_clients(coach_id=coach_id)
        return jsonify({"clients": clients}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500