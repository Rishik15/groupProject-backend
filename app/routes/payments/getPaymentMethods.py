from flask import jsonify, session
from app.routes.payments import payments_bp
from app.services.payments.get_Payment_Methods import get_payment_methods


@payments_bp.route("/payment-methods", methods=["GET"])
def get_payment_methods_route():
    """
Get user payment methods
---
tags:
  - payments
responses:
  200:
    description: List of payment methods
    schema:
      type: array
      items:
        type: object
        properties:
          payment_method_id:
            type: integer
          card_last_four:
            type: string
          card_brand:
            type: string
          expiry_month:
            type: integer
          expiry_year:
            type: integer
          is_default:
            type: boolean
  401:
    description: Unauthorized
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    methods = get_payment_methods(user_id)
    return jsonify(methods), 200