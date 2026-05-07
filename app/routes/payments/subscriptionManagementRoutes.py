from flask import jsonify, session

from app.routes.payments import payments_bp
from app.services.payments.subscriptionManagementService import (
    cancel_client_subscription,
    get_active_client_subscription_contract,
    start_client_subscription,
)


@payments_bp.route("/subscription", methods=["GET"])
def get_client_subscription_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        contract = get_active_client_subscription_contract(user_id)
        return jsonify({"contract": contract}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/subscription/start", methods=["PATCH"])
def start_client_subscription_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        contract = start_client_subscription(user_id)

        return (
            jsonify(
                {
                    "message": "Monthly subscription started successfully",
                    "contract": contract,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/subscription/cancel", methods=["PATCH"])
def cancel_client_subscription_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        contract = cancel_client_subscription(user_id)

        return (
            jsonify(
                {
                    "message": "Monthly subscription cancelled successfully",
                    "contract": contract,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
