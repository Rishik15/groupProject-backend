from flask import jsonify, session
from . import payments_bp
from app.services.payments.get_Payment_History import get_payment_history
from datetime import datetime


def format_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


@payments_bp.route("/history", methods=["GET"])
def get_payment_history_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    payments = get_payment_history(user_id)

    result = []
    for p in payments:
        result.append({
            "payment_id":       p["payment_id"],
            "amount":           float(p["amount"]),
            "currency":         p["currency"],
            "status":           p["status"],
            "payment_type":     p["payment_type"],
            "description":      p["description"],
            "paid_at":          format_datetime(p["paid_at"]),
            "coach": {
                "coach_id":    p["coach_id"],
                "first_name":  p["coach_first_name"],
                "last_name":   p["coach_last_name"],
            } if p["coach_id"] else None,
            "payment_method": {
                "card_brand":     p["card_brand"],
                "card_last_four": p["card_last_four"],
                "expiry_month":   p["expiry_month"],
                "expiry_year":    p["expiry_year"],
            } if p["card_brand"] else None,
        })

    return jsonify(result), 200