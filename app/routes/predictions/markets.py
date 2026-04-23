from flask import jsonify, request, session
from . import predictions_bp
from app.services.predictions.markets import (
    get_open_prediction_markets,
    create_prediction_market,
)


@predictions_bp.route("/markets/open", methods=["GET"])
def get_open_markets_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        markets = get_open_prediction_markets(user_id)

        return jsonify({
            "message": "success",
            "markets": markets
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/markets", methods=["POST"])
def create_prediction_market_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        title = data.get("title")
        goal_text = data.get("goal_text")
        end_date = data.get("end_date")

        if not title:
            return jsonify({"error": "title is required"}), 400

        if not goal_text:
            return jsonify({"error": "goal_text is required"}), 400

        if not end_date:
            return jsonify({"error": "end_date is required"}), 400

        market = create_prediction_market(
            creator_user_id=user_id,
            title=title,
            goal_text=goal_text,
            end_date=end_date
        )

        return jsonify({
            "message": "success",
            "market": market
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500