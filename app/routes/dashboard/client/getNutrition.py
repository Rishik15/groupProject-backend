from . import dashboard_client_bp
from flask import session
from app.services.dashboard.client.getDailyNutrition import getNutrition


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@dashboard_client_bp.route("/nutrition", methods=["GET"])
def get_daily_nutrition_route():
    """
    Get daily nutrition
    ---
    tags:
      - dashboard-client
    responses:
      200:
        description: Nutrition data
      401:
        description: Unauthorized
    """
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    data = getNutrition(
        user_id=int(user_id),
        user_timezone=_get_session_timezone(),
    )

    return data, 200
