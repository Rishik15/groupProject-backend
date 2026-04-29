from . import contract_bp
from flask import session, request, jsonify

from app.services.contracts.client_Contracts import requestContract
from app.services.contracts.contract_Status import get_contract_status


@contract_bp.route("/requestContract", methods=["POST"])
def requestContractRoute():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}

    coach_id = data.get("coach_id")
    is_recurring = data.get("is_recurring")
    training_reason = data.get("training_reason")
    preferred_schedule = data.get("preferred_schedule", "")
    notes = data.get("notes", "")

    payment_method_id = data.get("payment_method_id")
    card_number = data.get("card_number")
    card_brand = data.get("card_brand")
    expiry_month = data.get("expiry_month")
    expiry_year = data.get("expiry_year")

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    if is_recurring is None:
        return jsonify({"error": "is_recurring is required"}), 400

    if not training_reason:
        return jsonify({"error": "training_reason is required"}), 400

    if not payment_method_id:
        if not card_number:
            return jsonify({"error": "card_number is required"}), 400

        if not card_brand:
            return jsonify({"error": "card_brand is required"}), 400

        if not expiry_month:
            return jsonify({"error": "expiry_month is required"}), 400

        if not expiry_year:
            return jsonify({"error": "expiry_year is required"}), 400

    try:
        requestContract(
            user_id=int(user_id),
            coach_id=int(coach_id),
            is_recurring=bool(is_recurring),
            training_reason=training_reason,
            preferred_schedule=preferred_schedule,
            notes=notes,
            payment_method_id=payment_method_id,
            card_number=card_number,
            card_brand=card_brand,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
        )

        return jsonify({"message": "Contract request sent successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
