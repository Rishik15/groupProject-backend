from flask import session
from . import dashboard_client_bp
from app.services.dashboard.client.getWeight import get_user_weight


@dashboard_client_bp.route("/weight", methods=["GET"])
def get_weight_metrics():
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    weekly = get_user_weight(user_id)

    return {"weekly": weekly}, 200
