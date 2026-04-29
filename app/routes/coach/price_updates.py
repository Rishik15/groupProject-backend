from flask import jsonify, session
from . import coach_bp
from app.services.coach.coach_price_updates import get_my_price_updates


@coach_bp.route("/price-updates/my", methods=["GET"])
def get_my_price_updates_route():
    try:
        coach_id = session.get("user_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        updates = get_my_price_updates(int(coach_id))

        return (
            jsonify(
                {
                    "message": "success",
                    "updates": updates,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
