from flask import session
from . import dashboard_client_bp
from app.services.dashboard.client.getWorkouts import get_workout_completion_service


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@dashboard_client_bp.route("/workout-completion", methods=["GET"])
def get_workout_completion():
    """
    Get workout completion metrics
    ---
    tags:
      - dashboard-client
    responses:
      200:
        description: Workout completion data
      401:
        description: Unauthorized
    """
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    data = get_workout_completion_service(
        user_id=int(user_id),
        user_timezone=_get_session_timezone(),
    )

    return data, 200
