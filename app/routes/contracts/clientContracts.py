from . import contract_bp
from flask import session, request, jsonify
from app.services.contracts.client_Contracts import requestContract


@contract_bp.route("/requestContract", methods=["POST"])
def requestContractRoute():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()
    coach_id = data.get("coach_id")
    is_recurring = data.get("is_recurring", False)
    payment_method_id = data.get("payment_method_id")
    card_number = data.get("card_number")
    card_brand = data.get("card_brand")
    expiry_month = data.get("expiry_month")
    expiry_year = data.get("expiry_year")

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    if not payment_method_id and not all([card_number, card_brand, expiry_month, expiry_year]):
        return jsonify({"error": "Either payment_method_id or full card details are required"}), 400

    try:
        requestContract(
            user_id=user_id,
            coach_id=coach_id,
            is_recurring=is_recurring,
            payment_method_id=payment_method_id,
            card_number=card_number,
            card_brand=card_brand,
            expiry_month=int(expiry_month) if expiry_month else None,
            expiry_year=int(expiry_year) if expiry_year else None
        )
        return jsonify({"message": "Contract request sent successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500