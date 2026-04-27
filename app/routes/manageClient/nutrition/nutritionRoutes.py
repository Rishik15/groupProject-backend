from . import manage_nutrition_bp
from flask import session, request, jsonify

from app.utils.Contract.getClientId import getClientIdFromContract
from app.services.nutrition.get_Nutrition_Today import get_nutrition_today
from app.services.nutrition.get_Weekly_Calories import get_weekly_calories


def get_client_id_from_contract():
    coach_id = session.get("user_id")

    if not coach_id:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    contract_id = request.args.get("contract_id", type=int)

    if not contract_id:
        return None, (jsonify({"error": "contract_id is required"}), 400)

    client_id = getClientIdFromContract(contract_id, coach_id)

    if not client_id:
        return None, (jsonify({"error": "Invalid contract or access denied"}), 404)

    return int(client_id), None


@manage_nutrition_bp.route("/getNutritionToday", methods=["GET"])
def get_nutrition_today_contract():
    try:
        client_id, error = get_client_id_from_contract()

        if error:
            return error

        result = get_nutrition_today(client_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/getWeeklyCaloriesSummary", methods=["GET"])
def get_weekly_calories_summary_contract():
    try:
        client_id, error = get_client_id_from_contract()

        if error:
            return error

        result = get_weekly_calories(client_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
