from flask import jsonify, request, session
from . import predictions_bp
from app.services.predictions.markets import (
    get_open_prediction_markets,
    create_prediction_market,
    get_my_prediction_markets,
    get_prediction_summary,
    get_completed_prediction_markets,
    get_prediction_leaderboard,
    close_prediction_market,
    request_prediction_market_cancellation,
)


@predictions_bp.route("/markets/open", methods=["GET"])
def get_open_prediction_markets_route():
    """
Get open prediction markets
---
tags:
  - predictions
responses:
  200:
    description: List of open markets
    schema:
      type: object
      properties:
        message:
          type: string
        markets:
          type: array
          items:
            type: object
            properties:
              market_id:
                type: integer
              creator_user_id:
                type: integer
              creator_name:
                type: string
              creator_email:
                type: string
              title:
                type: string
              goal_text:
                type: string
              end_date:
                type: string
                format: date-time
              status:
                type: string
              review_status:
                type: string
              total_bets:
                type: integer
              total_points:
                type: integer
              yes_bets:
                type: integer
              no_bets:
                type: integer
              yes_points:
                type: integer
              no_points:
                type: integer
  401:
    description: Unauthorized
    """
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        markets = get_open_prediction_markets(int(user_id))

        return jsonify({
            "message": "success",
            "markets": markets
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/markets", methods=["POST"])
def create_prediction_market_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

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
            creator_user_id=int(user_id),
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


@predictions_bp.route("/me/markets", methods=["GET"])
def get_my_prediction_markets_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        markets = get_my_prediction_markets(int(user_id))

        return jsonify({
            "message": "success",
            "markets": markets
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/summary", methods=["GET"])
def get_prediction_summary_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        summary = get_prediction_summary(int(user_id))

        return jsonify({
            "message": "success",
            "summary": summary
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/completed", methods=["GET"])
def get_completed_prediction_markets_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        markets = get_completed_prediction_markets(int(user_id))

        return jsonify({
            "message": "success",
            "markets": markets
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/leaderboard", methods=["GET"])
def get_prediction_leaderboard_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        leaderboard = get_prediction_leaderboard(int(user_id))

        return jsonify({
            "message": "success",
            "leaderboard": leaderboard
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/markets/close", methods=["PATCH"])
def close_prediction_market_route():
    """
Close prediction market
---
tags:
  - predictions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - market_id
      properties:
        market_id:
          type: integer
responses:
  200:
    description: Market closed
  400:
    description: Invalid input
  403:
    description: Forbidden
    """
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        market_id = data.get("market_id")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        market = close_prediction_market(
            user_id=int(user_id),
            market_id=market_id
        )

        return jsonify({
            "message": "success",
            "market": market
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/markets/cancel-request", methods=["PATCH"])
def request_prediction_market_cancellation_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        market_id = data.get("market_id")
        reason = data.get("reason")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        if not reason or not str(reason).strip():
            return jsonify({"error": "reason is required"}), 400

        market = request_prediction_market_cancellation(
            user_id=int(user_id),
            market_id=market_id,
            reason=reason
        )

        return jsonify({
            "message": "success",
            "cancel_request": {
                "market_id": market["market_id"],
                "status": market["cancel_request_status"],
                "reason": market["cancel_request_reason"]
            },
            "market": market
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500