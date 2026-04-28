from flask import jsonify, request, session

from . import nutrition_bp
from app.services.nutrition.setGoals import (
    get_user_nutrition_goals,
    upsert_user_nutrition_goals,
)


def parse_nullable_int(value):
    if value is None or value == "":
        return None

    try:
        return int(value)
    except ValueError:
        return None


@nutrition_bp.route("/goals", methods=["GET"])
def get_goals():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    goals = get_user_nutrition_goals(user_id)

    return (
        jsonify(
            {
                "goals": goals,
            }
        ),
        200,
    )


@nutrition_bp.route("/goals", methods=["POST"])
def save_goals():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}

    calories_target = parse_nullable_int(data.get("calories_target"))
    protein_target = parse_nullable_int(data.get("protein_target"))
    carbs_target = parse_nullable_int(data.get("carbs_target"))
    fat_target = parse_nullable_int(data.get("fat_target"))

    if (
        calories_target is None
        and protein_target is None
        and carbs_target is None
        and fat_target is None
    ):
        return jsonify({"error": "At least one nutrition goal is required"}), 400

    goals = upsert_user_nutrition_goals(
        user_id=user_id,
        calories_target=calories_target,
        protein_target=protein_target,
        carbs_target=carbs_target,
        fat_target=fat_target,
    )

    return (
        jsonify(
            {
                "message": "Nutrition goals saved successfully",
                "goals": goals,
            }
        ),
        200,
    )
