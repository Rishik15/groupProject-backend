from flask import jsonify, request, session
from . import payments_bp
from app.services.payments.delete_Payment_Method import delete_payment_method


@payments_bp.route("/payment-methods/delete", methods=["DELETE"])
def delete_payment_method_route():
    """
Delete payment method
---
tags:
  - payments
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - payment_method_id
      properties:
        payment_method_id:
          type: integer
responses:
  200:
    description: Payment method deleted
  400:
    description: Missing payment_method_id
  401:
    description: Unauthorized
  404:
    description: Not found
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    payment_method_id = data.get("payment_method_id")

    if not payment_method_id:
        return jsonify({"error": "payment_method_id is required"}), 400

    try:
        delete_payment_method(user_id, payment_method_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Payment method deleted successfully"}), 200