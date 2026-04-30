from . import onboard_bp
from flask import jsonify, session, request
from datetime import datetime
from app.services.onboarding import onboardUser


@onboard_bp.route("/", methods=["POST"])
def onboardSurvey():
    """
Submit onboarding survey
---
tags:
  - onboarding
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - weight
        - height
        - dob
      properties:
        weight:
          type: number
        height:
          type: number
        dob:
          type: string
        goal_weight:
          type: number
        profile_picture:
          type: string
responses:
  200:
    description: Onboarding completed
  400:
    description: Missing required fields
  401:
    description: Unauthorized
"""
    try:
        data = request.get_json() or {}

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        dob_value = data.get("dob")
        date = datetime.fromisoformat(dob_value) if dob_value else datetime.now()

        weight = data.get("weight")
        height = data.get("height")
        goal_weight = (
            data.get("goal_weight") if data.get("goal_weight") is not None else weight
        )
        profile_picture = data.get("profile_picture")

        required_fields = [weight, height, dob_value]

        if any(field is None for field in required_fields):
            return (
                jsonify({"error": "weight, height, date of birth are required fields"}),
                400,
            )

        onboardUser.onboardClientSurvey(
            user_id,
            profile_picture,
            weight,
            height,
            goal_weight,
            date,
        )

        return jsonify({"message": "Client onboarding completed successfully"}), 200

    except Exception as e:
        raise e
