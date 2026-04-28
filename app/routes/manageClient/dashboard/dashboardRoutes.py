from flask import session, request
from . import manage_dashboard_bp
from app.services.dashboard.client.getUserMetrics import userMetrics
from app.services.dashboard.client.getCalories import get_calories_metrics_service
from app.services.dashboard.client.getDailyNutrition import getNutrition
from app.services.dashboard.client.getWeight import get_user_weight
from app.services.dashboard.client.getWorkouts import get_workout_completion_service
from app.utils.Contract.getClientId import getClientIdFromContract


def get_client_id_from_contract():
    coach_id = session.get("user_id")
    if not coach_id:
        return None, ({"error": "Unauthorized"}, 401)

    contract_id = request.args.get("contract_id", type=int)
    if not contract_id:
        return None, ({"error": "contract_id is required"}, 400)

    client_id = getClientIdFromContract(contract_id, coach_id)

    if not client_id:
        return None, ({"error": "Invalid contract or access denied"}, 404)

    return client_id, None


@manage_dashboard_bp.route("/metrics", methods=["GET"])
def getMetrics():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    return userMetrics(client_id), 200


@manage_dashboard_bp.route("/calories", methods=["GET"])
def get_calories_metrics():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    weekly = get_calories_metrics_service(client_id)
    return {"weekly": weekly}, 200


@manage_dashboard_bp.route("/nutrition", methods=["GET"])
def get_daily_nutrition_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    data = getNutrition(client_id)
    return data, 200


@manage_dashboard_bp.route("/weight", methods=["GET"])
def get_weight_metrics():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    weekly = get_user_weight(client_id)
    return {"weekly": weekly}, 200


@manage_dashboard_bp.route("/workout-completion", methods=["GET"])
def get_workout_completion():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    data = get_workout_completion_service(client_id)
    return data, 200
