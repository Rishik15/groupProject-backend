from . import onboard_bp
from flask import jsonify, session, request
from datetime import datetime
from app.services.onboarding.coachApplication import addCoachApplication


@onboard_bp.route("/coachApplication", methods=["POST"])
def coach_application():
    try:
        data = request.get_json() or {}

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        coach_description = data.get("coach_description")
        desired_price = data.get("price")

        if coach_description is None or desired_price is None:
            return jsonify({"error": "coach_description and price are required"}), 400

        addCoachApplication(
            user_id=user_id,
            years_experience=data.get("years_experience"),
            coach_description=coach_description,
            desired_price=desired_price,
            metadata=data,
        )

        return jsonify({"message": "Coach application submitted successfully"}), 200

    except Exception as e:
        raise e
