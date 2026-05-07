from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.get_Coach_Profile import get_coach_profile


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@coach_bp.route("/profile", methods=["POST"])
def get_coach_profile_route():
    """
    Get coach profile
    ---
    tags:
      - coach
    parameters:
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            coach_id:
              type: integer
    responses:
      200:
        description: Full coach profile
      400:
        description: Missing coach_id
      404:
        description: Coach not found
    """
    data = request.get_json(silent=True) or {}
    coach_id = data.get("coach_id") or session.get("user_id")

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    try:
        profile = get_coach_profile(
            coach_id=int(coach_id),
            user_timezone=_get_session_timezone(),
        )

        if not profile:
            return jsonify({"error": "Coach not found"}), 404

        return jsonify({"coach": profile}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
