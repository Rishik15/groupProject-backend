from . import onboard_bp
# from app.services.
from flask import jsonify, session, request

from app.services.onboarding import onboardUser

@onboard_bp.route("/", methods=["POST"])
def onboardSurvey():

    data = request.get_json()

    u_id = session.get("user_id")
    role = session.get("role")

    if not u_id or not role:
        return jsonify({"error": "Unauthorized"}), 401
    u_id = int(u_id)


    if role == 'client' or role == 'admin':
        try:
            onboardUser.onboardClientSurvey(
                u_id, 
                data["profile_picture"], 
                data["weight"],
                data["height"],
                data["goal_weight"]
                )
            return jsonify({"message": "Onboarding completed successfully"}), 200
        except Exception as e: 
            raise e
    elif role == 'coach':
        try:
            onboardUser.onboardClientSurvey(
                u_id, 
                data["profile_picture"],
                data["weight"],
                data["height"],
                data["goal_weight"]
            )

            onboardUser.onboardCoachSurvey(
                u_id, 
                data["coach_description"],
                data["price"]
            )
            return jsonify({"message": "Onboarding completed successfully"}), 200
        except Exception as e: 
            raise e
 
    else: 
        return jsonify({"error": "Invalid role"}), 400