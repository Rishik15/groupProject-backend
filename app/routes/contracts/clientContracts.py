from flask import session, request, jsonify

from . import contract_bp
from app.services.contracts.client_Contracts import requestContract


def parse_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value == 1

    if isinstance(value, str):
        return value.strip().lower() in ["true", "1", "yes", "y"]

    return False


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@contract_bp.route("/requestContract", methods=["POST"])
def requestContractRoute():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}

    coach_id = data.get("coach_id")
    is_recurring = data.get("is_recurring")
    training_reason = data.get("training_reason")
    goals = data.get("goals")
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

    if not goals:
        return jsonify({"error": "goals is required"}), 400

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
        result = requestContract(
            user_id=int(user_id),
            coach_id=int(coach_id),
            is_recurring=parse_bool(is_recurring),
            training_reason=training_reason.strip(),
            goals=goals.strip(),
            preferred_schedule=preferred_schedule.strip(),
            notes=notes.strip(),
            payment_method_id=int(payment_method_id) if payment_method_id else None,
            card_number=card_number,
            card_brand=card_brand,
            expiry_month=int(expiry_month) if expiry_month else None,
            expiry_year=int(expiry_year) if expiry_year else None,
            user_timezone=_get_session_timezone(),
        )

        return (
            jsonify(
                {
                    "message": "Contract request sent successfully",
                    "contract_id": result.get("contract_id"),
                    "payment_method_id": result.get("payment_method_id"),
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
