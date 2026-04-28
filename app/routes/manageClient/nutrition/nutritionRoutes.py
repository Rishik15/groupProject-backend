from . import manage_nutrition_bp
from flask import session, request, jsonify

from app.utils.Contract.getClientId import getClientIdFromContract
from app.services.nutrition.get_Nutrition_Today import get_nutrition_today
from app.services.nutrition.get_Weekly_Calories import get_weekly_calories
from app.services.nutrition.setGoals import (
    get_user_nutrition_goals,
    upsert_user_nutrition_goals,
)


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


def to_number_or_none(value):
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


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


@manage_nutrition_bp.route("/goals", methods=["GET"])
def get_nutrition_goals_contract():
    try:
        client_id, error = get_client_id_from_contract()

        if error:
            return error

        goals = get_user_nutrition_goals(client_id)

        return jsonify({"goals": goals}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/goals", methods=["POST", "PATCH"])
def set_nutrition_goals_contract():
    try:
        client_id, error = get_client_id_from_contract()

        if error:
            return error

        data = request.get_json() or {}

        calories_target = to_number_or_none(data.get("calories_target"))
        protein_target = to_number_or_none(data.get("protein_target"))
        carbs_target = to_number_or_none(data.get("carbs_target"))
        fat_target = to_number_or_none(data.get("fat_target"))

        if (
            calories_target is None
            and protein_target is None
            and carbs_target is None
            and fat_target is None
        ):
            return jsonify({"error": "Enter at least one nutrition goal"}), 400

        goals = upsert_user_nutrition_goals(
            user_id=client_id,
            calories_target=calories_target,
            protein_target=protein_target,
            carbs_target=carbs_target,
            fat_target=fat_target,
        )

        return jsonify({"message": "Nutrition goals updated", "goals": goals}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
