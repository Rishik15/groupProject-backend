from flask import session
from . import dashboard_client_bp
from app.services.dashboard.client.getCalories import get_calories_metrics_service


@dashboard_client_bp.route("/calories", methods=["GET"])
def get_calories_metrics():
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    weekly = get_calories_metrics_service(user_id)

    return {"weekly": weekly}, 200
