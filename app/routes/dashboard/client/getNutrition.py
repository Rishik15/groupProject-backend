from . import dashboard_client_bp
from flask import session
from app.services.dashboard.client.getDailyNutrition import getNutrition


@dashboard_client_bp.route("/nutrition", methods=["GET"])
def get_daily_nutrition_route():
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    data = getNutrition(user_id)

    return data, 200
