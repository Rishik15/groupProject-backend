from flask import jsonify, request, session

from app.routes.manageClient.nutrition import manage_nutrition_bp
from app.utils.Contract.getClientId import getClientIdFromContract
from app.services import run_query

from app.services.nutrition.assign_Meal_Plan import assign_meal_plan
from app.services.nutrition.create_Meal_Plan import create_meal_plan
from app.services.nutrition.delete_Meal_Plan import delete_meal_plan
from app.services.nutrition.get_Meal_Plan_Details import get_meal_plan_detail
from app.services.nutrition.get_Meal_Plans import get_meal_plan_library
from app.services.nutrition.get_My_Meal_Plans import get_my_meal_plans
from app.services.nutrition.update_Meal_Plan import update_meal_plan


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


def coach_can_access_plan(client_id, meal_plan_id, allow_system_plan=True):
    allowed_user_ids = [client_id]

    if allow_system_plan:
        allowed_user_ids.append(1)

    placeholders = []
    params = {"meal_plan_id": meal_plan_id}

    for index, user_id in enumerate(allowed_user_ids):
        key = f"user_id_{index}"
        placeholders.append(f":{key}")
        params[key] = user_id

    result = run_query(
        f"""
        SELECT meal_plan_id
        FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id
        AND user_id IN ({", ".join(placeholders)})
        """,
        params,
        fetch=True,
        commit=False,
    )

    return bool(result)


@manage_nutrition_bp.route("/meal-plans", methods=["GET"])
def manage_meal_plans_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    try:
        plans = get_meal_plan_library()
        return jsonify({"meal_plans": plans}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/meal-plans/detail", methods=["GET"])
def manage_meal_plan_detail_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    meal_plan_id = request.args.get("meal_plan_id", type=int)

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        has_access = coach_can_access_plan(
            client_id=client_id,
            meal_plan_id=meal_plan_id,
            allow_system_plan=True,
        )

        if not has_access:
            return jsonify({"error": "Meal plan not found or access denied"}), 404

        detail = get_meal_plan_detail(meal_plan_id)

        if not detail:
            return jsonify({"error": "Meal plan not found"}), 404

        return jsonify(detail), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/meal-plans/my-plans", methods=["GET"])
def manage_get_client_meal_plans_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    try:
        plans = get_my_meal_plans(client_id)
        return jsonify(plans), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/meal-plans/create", methods=["POST"])
def manage_create_meal_plan_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    data = request.get_json() or {}

    plan_name = data.get("plan_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    meals = data.get("meals", [])

    if not plan_name:
        return jsonify({"error": "plan_name is required"}), 400

    try:
        meal_plan_id = create_meal_plan(
            client_id,
            plan_name,
            meals,
            start_date,
            end_date,
        )

        return (
            jsonify(
                {
                    "message": "Meal plan created successfully",
                    "meal_plan_id": meal_plan_id,
                }
            ),
            201,
        )

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": f"Meal plan '{plan_name}' already exists"}), 409

        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/meal-plans/assign", methods=["POST"])
def manage_assign_meal_plan_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    data = request.get_json() or {}

    meal_plan_id = data.get("meal_plan_id")
    start_date = data.get("start_date")
    force = data.get("force", False)

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        has_access = coach_can_access_plan(
            client_id=client_id,
            meal_plan_id=meal_plan_id,
            allow_system_plan=True,
        )

        if not has_access:
            return jsonify({"error": "Meal plan not found or access denied"}), 404

        new_plan_id = assign_meal_plan(
            client_id,
            int(meal_plan_id),
            start_date,
            force,
        )

        return (
            jsonify(
                {
                    "message": "Meal plan assigned successfully",
                    "meal_plan_id": new_plan_id,
                }
            ),
            201,
        )

    except ValueError as e:
        error_str = str(e)

        if error_str.startswith("EXISTING_PLAN:"):
            existing_plan_name = error_str.split("EXISTING_PLAN:")[1]

            return (
                jsonify(
                    {
                        "error": "existing_plan",
                        "existing_plan_name": existing_plan_name,
                        "message": f"'{existing_plan_name}' is already assigned for this week. Send force=true to replace it.",
                    }
                ),
                409,
            )

        return jsonify({"error": error_str}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/meal-plans/update", methods=["PUT"])
def manage_update_meal_plan_route():
    client_id, error = get_client_id_from_contract()

    if error:
        return error

    data = request.get_json() or {}

    meal_plan_id = data.get("meal_plan_id")

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        has_access = coach_can_access_plan(
            client_id=client_id,
            meal_plan_id=meal_plan_id,
            allow_system_plan=False,
        )

        if not has_access:
            return jsonify({"error": "Meal plan not found or access denied"}), 404

        result = update_meal_plan(
            user_id=client_id,
            meal_plan_id=int(meal_plan_id),
            plan_name=data.get("plan_name"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            add_meals=data.get("add_meals", []),
            remove_meals=data.get("remove_meals", []),
            update_servings=data.get("update_servings", []),
        )

        return (
            jsonify(
                {
                    "message": "Meal plan updated successfully",
                    "meal_plan_id": result["meal_plan_id"],
                    "total_calories": result["total_calories"],
                }
            ),
            200,
        )

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "A meal plan with this name already exists"}), 409

        return jsonify({"error": str(e)}), 500


@manage_nutrition_bp.route("/meal-plans/delete", methods=["DELETE"])
def manage_delete_meal_plan_route():
    client_id, error = get_client_id_from_contract()
    if error:
        return error

    meal_plan_id = request.args.get("meal_plan_id", type=int)

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        delete_meal_plan(client_id, meal_plan_id)
        return jsonify({"message": "Meal plan deleted successfully"}), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500
