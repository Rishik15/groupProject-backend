from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.get_Coach_Profile import get_coach_profile


@coach_bp.route("/profile", methods=["POST"])
def get_coach_profile_route():
    data = request.get_json()
    coach_id = data.get("coach_id") or session.get("user_id")

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    try:
        profile = get_coach_profile(coach_id=coach_id)
        if not profile:
            return jsonify({"error": "Coach not found"}), 404
        return jsonify({"coach": profile}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500