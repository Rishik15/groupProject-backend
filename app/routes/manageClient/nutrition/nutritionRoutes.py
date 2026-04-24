from . import manage_nutrition_bp
from flask import session, request, jsonify
from app.services.nutrition import mealLogging
from app.utils.Contract.getClientId import getClientIdFromContract
from app.services.nutrition.getGoals import getNutritionGoals


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


@manage_nutrition_bp.route("/getLoggedMeals", methods=["GET"])
def get_logged_meals_contract():
    try:
        if "user_id" not in session:
            return {"error": "Unauthorized"}, 401

        coach_id = session.get("user_id")

        contract_id = request.args.get("contract_id")
        start_dt = request.args.get("start_datetime")
        end_dt = request.args.get("end_datetime")

        if not contract_id:
            return {"error": "contract_id required"}, 400

        contract_id = int(contract_id)

        client_id, error = get_client_id_from_contract()
        if error:
            return error

        meals = mealLogging.getLoggedMeals(
            user_id=client_id, start_dt=start_dt, end_dt=end_dt
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "loggedMeals": meals if meals else [],
                }
            ),
            200,
        )

    except Exception as e:
        return {"error": str(e)}, 500
