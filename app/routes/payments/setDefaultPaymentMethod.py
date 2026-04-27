from flask import jsonify, request, session
from . import payments_bp
from app.services.payments.set_Default_Payment_Method import set_default_payment_method


@payments_bp.route("/payment-methods/set-default", methods=["PUT"])
def set_default_payment_method_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    payment_method_id = data.get("payment_method_id")

    if not payment_method_id:
        return jsonify({"error": "payment_method_id is required"}), 400

    try:
        set_default_payment_method(user_id, payment_method_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Default payment method updated successfully"}), 200