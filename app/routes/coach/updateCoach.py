from flask import jsonify, request, session

from app.services.coach.update_coach import update_coach_profile
from . import coach_bp


@coach_bp.route("/update", methods=["PATCH"])
def handle_update():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        result = update_coach_profile(int(user_id), data)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
