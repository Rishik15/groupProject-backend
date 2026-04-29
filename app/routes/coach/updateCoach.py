from flask import jsonify, request, session

from app.services.coach.update_coach import update_coach_profile
from . import coach_bp

@coach_bp.route("/update", methods=["PATCH"])
def handle_update():
    """
Update coach profile
---
tags:
  - coach
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      properties:
        price:
          type: number
        coach_description:
          type: string
responses:
  200:
    description: Profile updated
  400:
    description: Invalid input
  401:
    description: Unauthorized
    """
    try:
        user_id = session.get("user_id")
        data = request.get_json()

        result = update_coach_profile(user_id, data)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500