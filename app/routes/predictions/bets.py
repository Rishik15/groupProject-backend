from flask import jsonify, session
from . import predictions_bp
from app.services.predictions.bets import (
    place_prediction_bet,
    get_my_prediction_bets,
)


@predictions_bp.route("/bets", methods=["POST"])
def place_prediction_bet_route():
    from flask import request

    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        market_id = data.get("market_id")
        prediction_value = data.get("prediction_value")
        points_wagered = data.get("points_wagered")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        if not prediction_value:
            return jsonify({"error": "prediction_value is required"}), 400

        if points_wagered is None:
            return jsonify({"error": "points_wagered is required"}), 400

        bet = place_prediction_bet(
            predictor_user_id=user_id,
            market_id=market_id,
            prediction_value=prediction_value,
            points_wagered=points_wagered
        )

        return jsonify({
            "message": "success",
            "bet": bet
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/me/bets", methods=["GET"])
def get_my_prediction_bets_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        bets = get_my_prediction_bets(int(user_id))

        return jsonify({
            "message": "success",
            "bets": bets
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500