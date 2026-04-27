from flask import jsonify, session
from app.routes.payments import payments_bp
from app.services.payments.get_Payment_Methods import get_payment_methods


@payments_bp.route("/payment-methods", methods=["GET"])
def get_payment_methods_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    methods = get_payment_methods(user_id)
    return jsonify(methods), 200