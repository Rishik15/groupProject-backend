from . import onboard_bp
# from app.services.
from flask import jsonify, session, request

from app.services.onboarding import onboardUser

@onboard_bp.route("/", methods=["POST"])
def onboardSurvey():

    data = request.get_json()
    u_id = session["user_id"]
    u_id = int(u_id)

    role = session["role"]
    if role == 'client':
        try:
            onboardUser.onboardClientSurvey(
                u_id, 
                data["profile_picture"],
                data["weight"],
                data["height"],
                data["goal_weight"]
                )
        except Exception as e: 
            raise e
    elif role == 'coach':
        try:
            onboardUser.onboardCoachSurvey(
                u_id, 
                data["profile_picture"],
                data["weight"],
                data["height"],
                data["goal_weight"]
                )
        except Exception as e: 
            raise e