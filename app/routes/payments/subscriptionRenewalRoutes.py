from flask import current_app, jsonify, request

from app.routes.payments import payments_bp
from app.services.payments.subscriptionRenewalService import (
    process_due_subscription_payments,
)


@payments_bp.route("/process-subscriptions", methods=["POST"])
def process_subscriptions_route():
    cron_secret = current_app.config.get("CRON_SECRET")
    request_secret = request.headers.get("X-CRON-SECRET")

    if not cron_secret:
        return jsonify({"error": "CRON_SECRET is not configured"}), 500

    if request_secret != cron_secret:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        result = process_due_subscription_payments()

        return (
            jsonify(
                {
                    "message": "Subscription processing completed",
                    **result,
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.exception("Subscription cron failed")
        return jsonify({"error": str(e)}), 500
