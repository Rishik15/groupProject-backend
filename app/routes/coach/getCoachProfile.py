from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.get_Coach_Profile import get_coach_profile


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
    schema:
      type: object
      properties:
        coach:
          type: object
          properties:
            first_name:
              type: string
            last_name:
              type: string
            price:
              type: number
            coach_description:
              type: string
            avg_rating:
              type: number
            active_clients:
              type: integer
            certifications:
              type: array
              items:
                type: object
            availability:
              type: array
              items:
                type: object
  400:
    description: Missing coach_id
  404:
    description: Coach not found
    """
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