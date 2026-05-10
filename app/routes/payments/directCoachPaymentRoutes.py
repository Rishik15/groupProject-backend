from flask import jsonify, session

from app.routes.payments import payments_bp
from app.services.payments.directCoachPaymentService import pay_current_coach_now


@payments_bp.route("/pay-coach-now", methods=["POST"])
def pay_current_coach_now_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        payment = pay_current_coach_now(user_id)

        return (
            jsonify(
                {
                    "message": "Coach payment completed successfully",
                    "payment": payment,
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500