from flask import jsonify, request, session
from app.routes.payments import payments_bp
from app.services.payments.add_Payment_Method import add_payment_method


@payments_bp.route("/add-card", methods=["POST"])
def add_payment_method_route():
    """
Add payment method
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
        - card_number
        - card_brand
        - expiry_month
        - expiry_year
      properties:
        card_number:
          type: string
        card_brand:
          type: string
        expiry_month:
          type: integer
        expiry_year:
          type: integer
responses:
  201:
    description: Payment method added
  400:
    description: Invalid input
  401:
    description: Unauthorized
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    card_number = data.get("card_number")
    card_brand = data.get("card_brand")
    expiry_month = data.get("expiry_month")
    expiry_year = data.get("expiry_year")

    if not card_number or not card_brand or not expiry_month or not expiry_year:
        return jsonify({"error": "card_number, card_brand, expiry_month and expiry_year are required"}), 400

    card_last_four = str(card_number).replace(" ", "")[-4:]

    try:
        payment_method_id = add_payment_method(
            user_id=user_id,
            card_last_four=card_last_four,
            card_brand=card_brand,
            expiry_month=int(expiry_month),
            expiry_year=int(expiry_year)
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Payment method added successfully",
        "payment_method_id": payment_method_id
    }), 201